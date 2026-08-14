import json
import logging
import re
import uuid
from pathlib import Path

import requests
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.validators import validate_email
from django.http import FileResponse, Http404, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST

from .models import EbookAchat


logger = logging.getLogger(__name__)
PRIX_EBOOK = 2_000
KKIAPAY_STATUS_URL = (
    "https://api-sandbox.kkiapay.me/api/v1/transactions/status"
    if settings.KKIAPAY_SANDBOX
    else "https://api.kkiapay.me/api/v1/transactions/status"
)


def _optional_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        return None


def _diagnostic_context(public_id=None, session_id=None):
    try:
        DiagnosticReponse = apps.get_model("diagnostic", "DiagnosticReponse")
        DiagnosticEvenement = apps.get_model("diagnostic", "DiagnosticEvenement")
    except LookupError:
        return None, None, None
    diagnostic = None
    if public_id:
        diagnostic = DiagnosticReponse.objects.filter(public_id=public_id).first()
    if not diagnostic and session_id:
        diagnostic = DiagnosticReponse.objects.filter(session_id=session_id).first()
    resolved_session = diagnostic.session_id if diagnostic else session_id
    return diagnostic, resolved_session, DiagnosticEvenement


def _track_checkout(nom, diagnostic, session_id, EventModel):
    if not session_id or EventModel is None:
        return
    EventModel.objects.get_or_create(
        session_id=session_id,
        nom=nom,
        ecran="checkout",
        defaults={"reponse": diagnostic},
    )


@ensure_csrf_cookie
def vente_ebook(request):
    diagnostic_id = _optional_uuid(request.GET.get("diagnostic"))
    # Une session propre au checkout permet aussi de mesurer les achats directs,
    # même lorsqu'ils ne proviennent pas du diagnostic.
    diagnostic_session = _optional_uuid(request.GET.get("diagnostic_session")) or uuid.uuid4()
    diagnostic, diagnostic_session, EventModel = _diagnostic_context(
        diagnostic_id, diagnostic_session
    )
    _track_checkout("checkout_view", diagnostic, diagnostic_session, EventModel)
    return render(
        request,
        "ebook/vente_ebook.html",
        {
            "prix": PRIX_EBOOK,
            "kkiapay_public_key": settings.KKIAPAY_PUBLIC_KEY,
            "kkiapay_sandbox": settings.KKIAPAY_SANDBOX,
            "guarantee_enabled": settings.EBOOK_GUARANTEE_ENABLED,
            "guarantee_text": settings.EBOOK_GUARANTEE_TEXT,
            "diagnostic_id": str(diagnostic_id or ""),
            "diagnostic_session": str(diagnostic_session or ""),
        },
    )


@require_POST
def verifier_paiement(request):
    """Confirme statut et montant auprès de KKiaPay avant de livrer le PDF."""
    try:
        if len(request.body) > 8_192:
            raise ValueError("Requête trop volumineuse.")
        data = json.loads(request.body.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("Format invalide.")

        transaction_id = str(data.get("transactionId", "")).strip()[:120]
        email = str(data.get("email", "")).strip().lower()[:254]
        prenom = str(data.get("prenom", "")).strip()[:100]
        diagnostic_id = _optional_uuid(data.get("diagnosticId"))
        diagnostic_session = _optional_uuid(data.get("diagnosticSession"))
        diagnostic, diagnostic_session, EventModel = _diagnostic_context(
            diagnostic_id, diagnostic_session
        )
        if not re.fullmatch(r"[A-Za-z0-9_-]{5,120}", transaction_id):
            raise ValueError("Référence de paiement invalide.")
        validate_email(email)
        if not all(
            [
                settings.KKIAPAY_PUBLIC_KEY,
                settings.KKIAPAY_PRIVATE_KEY,
                settings.KKIAPAY_SECRET_KEY,
            ]
        ):
            logger.error("Configuration KKiaPay incomplète")
            return JsonResponse(
                {
                    "success": False,
                    "error": "Le paiement est momentanément indisponible.",
                },
                status=503,
            )

        _track_checkout("payment_started", diagnostic, diagnostic_session, EventModel)

        response = requests.post(
            KKIAPAY_STATUS_URL,
            json={"transactionId": transaction_id},
            headers={
                "x-api-key": settings.KKIAPAY_PUBLIC_KEY,
                "x-private-key": settings.KKIAPAY_PRIVATE_KEY,
                "x-secret-key": settings.KKIAPAY_SECRET_KEY,
                "Content-Type": "application/json",
            },
            timeout=15,
        )
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise TypeError("Réponse KKiaPay invalide")

        try:
            montant_confirme = int(result.get("amount", 0))
        except (TypeError, ValueError):
            montant_confirme = 0
        paiement_valide = (
            result.get("status") == "SUCCESS" and montant_confirme == PRIX_EBOOK
        )
        if not paiement_valide:
            EbookAchat.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={
                    "email": email,
                    "prenom": prenom,
                    "montant": montant_confirme or PRIX_EBOOK,
                    "statut": "echec",
                    "diagnostic": diagnostic,
                    "diagnostic_session_id": diagnostic_session,
                },
            )
            return JsonResponse(
                {
                    "success": False,
                    "error": "Le paiement n’a pas pu être confirmé. Aucun accès n’a été délivré.",
                },
                status=400,
            )

        achat, _ = EbookAchat.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                "email": email,
                "prenom": prenom,
                "montant": PRIX_EBOOK,
                "statut": "paye",
                "date_paiement": timezone.now(),
                "diagnostic": diagnostic,
                "diagnostic_session_id": diagnostic_session,
            },
        )
        if not achat.email_envoye:
            try:
                envoyer_ebook_par_email(achat, request=request)
            except Exception:
                logger.exception(
                    "Échec d’envoi de l’ebook pour la transaction %s",
                    transaction_id,
                )
            else:
                achat.email_envoye = True
                achat.save(update_fields=["email_envoye"])

        if diagnostic:
            diagnostic.ebook_achete = True
            diagnostic.save(update_fields=["ebook_achete"])
        _track_checkout("purchase", diagnostic, diagnostic_session, EventModel)

        return JsonResponse(
            {
                "success": True,
                "redirect": reverse(
                    "page_merci", kwargs={"token": achat.token_telechargement}
                ),
            }
        )
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError, ValidationError):
        return JsonResponse(
            {"success": False, "error": "Vérifiez les informations transmises."},
            status=400,
        )
    except requests.RequestException:
        logger.exception("KKiaPay est indisponible pendant la vérification")
        return JsonResponse(
            {
                "success": False,
                "error": "La confirmation du paiement prend plus de temps que prévu. Réessayez sans repayer.",
            },
            status=502,
        )
    except (TypeError, KeyError, AttributeError):
        logger.exception("Réponse KKiaPay inattendue")
        return JsonResponse(
            {
                "success": False,
                "error": "La confirmation n’a pas abouti. Réessayez sans repayer.",
            },
            status=502,
        )
    except Exception:
        logger.exception("Erreur interne pendant la livraison de l’ebook")
        return JsonResponse(
            {
                "success": False,
                "error": "Une erreur interne est survenue. Réessayez sans repayer.",
            },
            status=500,
        )


def envoyer_ebook_par_email(achat, request=None):
    if request is not None:
        lien = request.build_absolute_uri(
            reverse(
                "telecharger_ebook", kwargs={"token": achat.token_telechargement}
            )
        )
    else:
        lien = (
            f"{settings.SITE_URL}"
            f"{reverse('telecharger_ebook', kwargs={'token': achat.token_telechargement})}"
        )

    html_message = render_to_string(
        "ebook/email_ebook.html",
        {"prenom": achat.prenom or "Client", "lien": lien},
    )
    message = EmailMultiAlternatives(
        subject="Votre ebook — De l’Expert au Consultant Professionnel",
        body=strip_tags(html_message),
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[achat.email],
    )
    message.attach_alternative(html_message, "text/html")
    message.send(fail_silently=False)


def page_merci(request, token):
    achat = get_object_or_404(
        EbookAchat, token_telechargement=token, statut="paye"
    )
    return render(
        request,
        "ebook/merci.html",
        {
            "achat": achat,
            "groupe_url": settings.DIAGNOSTIC_WHATSAPP_GROUP_URL,
            "groupe_nom": settings.DIAGNOSTIC_WHATSAPP_GROUP_NAME,
            "tracking_url": reverse("diagnostic:evenement"),
        },
    )


def telecharger_ebook(request, token):
    get_object_or_404(EbookAchat, token_telechargement=token, statut="paye")
    chemin = (
        Path(settings.MEDIA_ROOT)
        / "ebook"
        / "De_l_Expert_au_Consultant_Professionnel.pdf"
    )
    if not chemin.is_file():
        raise Http404("Fichier introuvable.")
    return FileResponse(
        chemin.open("rb"),
        as_attachment=True,
        filename="De_l_Expert_au_Consultant_Professionnel.pdf",
    )
