import json
import logging
import re
import uuid
from datetime import timedelta
from pathlib import Path

import requests
from django.apps import apps
from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.signing import salted_hmac
from django.core.validators import validate_email
from django.db import transaction
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from .models import EbookAchat, EbookTelechargementEvenement


logger = logging.getLogger(__name__)
KKIAPAY_STATUS_URL = (
    "https://api-sandbox.kkiapay.me/api/v1/transactions/status"
    if settings.KKIAPAY_SANDBOX
    else "https://api.kkiapay.me/api/v1/transactions/status"
)


def _ebook_price():
    return max(1, int(getattr(settings, "EBOOK_PRICE", 2_000)))


def _download_limit():
    return max(1, int(getattr(settings, "EBOOK_DOWNLOAD_MAX", 3)))


def _download_expiry_delta():
    hours = max(1, int(getattr(settings, "EBOOK_DOWNLOAD_EXPIRY_HOURS", 72)))
    return timedelta(hours=hours)


def _download_fingerprint(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    ip_address = forwarded.split(",", 1)[0].strip() or request.META.get(
        "REMOTE_ADDR", ""
    )
    if not ip_address:
        return ""
    return salted_hmac(
        "ebook.download.ip",
        ip_address,
        algorithm="sha256",
    ).hexdigest()


def _record_download_event(request, achat, resultat):
    EbookTelechargementEvenement.objects.create(
        achat=achat,
        resultat=resultat,
        compteur_apres=achat.nombre_telechargements,
        empreinte_ip=_download_fingerprint(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:255],
    )


def _unavailable_download_page(request, *, achat=None, status=410):
    return render(
        request,
        "ebook/merci.html",
        {
            "achat": achat,
            "telechargement_disponible": False,
            "support_email": settings.EBOOK_SUPPORT_EMAIL,
            "groupe_url": settings.DIAGNOSTIC_WHATSAPP_GROUP_URL,
            "groupe_nom": settings.DIAGNOSTIC_WHATSAPP_GROUP_NAME,
            "tracking_url": reverse("diagnostic:evenement"),
        },
        status=status,
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
            "prix": _ebook_price(),
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

        prix_attendu = _ebook_price()
        try:
            montant_confirme = int(result.get("amount", 0))
        except (TypeError, ValueError):
            montant_confirme = 0
        statut_confirme = str(result.get("status", "")).strip().upper()
        logger.info(
            "Vérification KKiaPay transaction=…%s statut=%s montant=%s attendu=%s sandbox=%s",
            transaction_id[-8:],
            statut_confirme or "ABSENT",
            montant_confirme,
            prix_attendu,
            settings.KKIAPAY_SANDBOX,
        )
        paiement_valide = (
            statut_confirme == "SUCCESS" and montant_confirme == prix_attendu
        )
        if not paiement_valide:
            logger.warning(
                "Paiement KKiaPay non confirmé transaction=…%s statut=%s montant=%s attendu=%s",
                transaction_id[-8:],
                statut_confirme or "ABSENT",
                montant_confirme,
                prix_attendu,
            )
            EbookAchat.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={
                    "email": email,
                    "prenom": prenom,
                    "montant": montant_confirme or prix_attendu,
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

        payment_time = timezone.now()
        with transaction.atomic():
            achat, created = EbookAchat.objects.select_for_update().get_or_create(
                transaction_id=transaction_id,
                defaults={
                    "email": email,
                    "prenom": prenom,
                    "montant": prix_attendu,
                    "statut": "paye",
                    "date_paiement": payment_time,
                    "expiration_telechargement": (
                        payment_time + _download_expiry_delta()
                    ),
                    "diagnostic": diagnostic,
                    "diagnostic_session_id": diagnostic_session,
                },
            )
            was_already_paid = not created and achat.statut == "paye"
            achat.email = email
            achat.prenom = prenom
            achat.montant = prix_attendu
            achat.statut = "paye"
            achat.diagnostic = diagnostic
            achat.diagnostic_session_id = diagnostic_session
            if not was_already_paid:
                achat.date_paiement = payment_time
                achat.expiration_telechargement = (
                    payment_time + _download_expiry_delta()
                )
                achat.nombre_telechargements = 0
                achat.dernier_telechargement_at = None
            elif achat.expiration_telechargement is None:
                achat.expiration_telechargement = (
                    payment_time + _download_expiry_delta()
                )
            achat.save()
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
    achat = EbookAchat.objects.filter(
        token_telechargement=token,
        statut="paye",
    ).first()
    if achat is None:
        return _unavailable_download_page(request, status=404)

    if achat.expiration_telechargement is None:
        achat.expiration_telechargement = timezone.now() + _download_expiry_delta()
        achat.save(update_fields=["expiration_telechargement"])

    telechargement_disponible = (
        achat.expiration_telechargement > timezone.now()
        and achat.nombre_telechargements < _download_limit()
    )
    return render(
        request,
        "ebook/merci.html",
        {
            "achat": achat,
            "telechargement_disponible": telechargement_disponible,
            "support_email": settings.EBOOK_SUPPORT_EMAIL,
            "groupe_url": settings.DIAGNOSTIC_WHATSAPP_GROUP_URL,
            "groupe_nom": settings.DIAGNOSTIC_WHATSAPP_GROUP_NAME,
            "tracking_url": reverse("diagnostic:evenement"),
        },
    )


@require_GET
def telecharger_ebook(request, token):
    chemin = Path(settings.EBOOK_FILE_PATH)

    with transaction.atomic():
        achat = EbookAchat.objects.select_for_update().filter(
            token_telechargement=token,
            statut="paye",
        ).first()
        if achat is None:
            return _unavailable_download_page(request, status=404)

        now = timezone.now()
        if achat.expiration_telechargement is None:
            achat.expiration_telechargement = now + _download_expiry_delta()
            achat.save(update_fields=["expiration_telechargement"])

        if now >= achat.expiration_telechargement:
            _record_download_event(
                request,
                achat,
                EbookTelechargementEvenement.Resultat.EXPIRE,
            )
            return _unavailable_download_page(request, achat=achat)

        if achat.nombre_telechargements >= _download_limit():
            _record_download_event(
                request,
                achat,
                EbookTelechargementEvenement.Resultat.LIMITE,
            )
            return _unavailable_download_page(request, achat=achat)

        if not chemin.is_file():
            _record_download_event(
                request,
                achat,
                EbookTelechargementEvenement.Resultat.FICHIER_ABSENT,
            )
            logger.error("PDF ebook absent du chemin configuré : %s", chemin)
            return _unavailable_download_page(request, achat=achat, status=503)

        achat.nombre_telechargements += 1
        achat.dernier_telechargement_at = now
        achat.save(
            update_fields=["nombre_telechargements", "dernier_telechargement_at"]
        )
        _record_download_event(
            request,
            achat,
            EbookTelechargementEvenement.Resultat.AUTORISE,
        )

    response = FileResponse(
        chemin.open("rb"),
        as_attachment=True,
        filename="De_l_Expert_au_Consultant_Professionnel.pdf",
    )
    response["Cache-Control"] = "private, no-store, max-age=0"
    response["Pragma"] = "no-cache"
    response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
    return response
