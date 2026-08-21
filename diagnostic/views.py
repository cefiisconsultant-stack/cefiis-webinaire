import json
import re
import uuid
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from django.apps import apps
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.urls import reverse
from django.utils import timezone
from django.utils.html import escape
from django.views.decorators.csrf import csrf_exempt, ensure_csrf_cookie
from django.views.decorators.http import require_GET, require_POST

from ebook.constants import PRIX_EBOOK

from .contenus import contenu_pour
from .countries import INDICATIFS, PAYS_AFRIQUE_FRANCOPHONE
from .models import DiagnosticEvenement, DiagnosticReponse
from .profils import analyse_pour


def _choice_values(choices):
    return {value for value, _ in choices}


def _text(data, key, limit=250):
    return escape(str(data.get(key, "")).strip())[:limit]


def _required_choice(data, key, choices):
    value = _text(data, key, 40)
    if value not in _choice_values(choices):
        raise ValueError(f"Réponse invalide pour « {key} ».")
    return value


def _optional_choice(data, key, choices):
    value = _text(data, key, 40)
    if value and value not in _choice_values(choices):
        raise ValueError(f"Réponse invalide pour « {key} ».")
    return value


def _uuid(value):
    try:
        return uuid.UUID(str(value))
    except (ValueError, TypeError, AttributeError):
        raise ValueError("Session de diagnostic invalide.")


def _json(request):
    if len(request.body) > 16_384:
        raise ValueError("Requête trop volumineuse.")
    try:
        data = json.loads(request.body.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError):
        raise ValueError("Données illisibles.")
    if not isinstance(data, dict):
        raise ValueError("Format invalide.")
    return data


def _bool(data, key):
    return data.get(key) is True


def _add_query(url, **params):
    parts = urlsplit(url)
    query = dict(parse_qsl(parts.query, keep_blank_values=True))
    query.update({key: str(value) for key, value in params.items() if value})
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def _same_origin(request):
    """Refuse une télémétrie envoyée explicitement depuis un autre site."""
    origin = request.headers.get("Origin", "")
    if not origin:
        return True
    try:
        return urlsplit(origin).netloc == request.get_host()
    except ValueError:
        return False


def _config():
    return {
        "ga4_id": getattr(settings, "GA4_MEASUREMENT_ID", ""),
        "ebook_url": getattr(settings, "DIAGNOSTIC_EBOOK_URL", "/ebook/"),
        "ebook_price": PRIX_EBOOK,
        "kkiapay_public_key": settings.KKIAPAY_PUBLIC_KEY,
        "kkiapay_sandbox": settings.KKIAPAY_SANDBOX,
        "groupe_url": getattr(
            settings,
            "DIAGNOSTIC_WHATSAPP_GROUP_URL",
            "https://chat.whatsapp.com/IJi96yhLhyYJjOPtWFKwtN",
        ),
        "temoignage": getattr(settings, "DIAGNOSTIC_TESTIMONIAL", ""),
        "garantie_active": getattr(settings, "EBOOK_GUARANTEE_ENABLED", False),
        "garantie_texte": getattr(settings, "EBOOK_GUARANTEE_TEXT", ""),
        "groupe_nom": getattr(
            settings,
            "DIAGNOSTIC_WHATSAPP_GROUP_NAME",
            "Cercle des Experts & Consultants | Cefiis",
        ),
    }


@require_GET
@ensure_csrf_cookie
def quiz(request):
    return render(
        request,
        "diagnostic/quiz.html",
        {"pays": PAYS_AFRIQUE_FRANCOPHONE, **_config()},
    )


@require_POST
def enregistrer(request):
    try:
        data = _json(request)
        prenom = _text(data, "prenom", 100)
        numero_national = re.sub(r"\D", "", _text(data, "numero_national", 24))
        pays = _text(data, "pays", 2).upper()
        indicatif = INDICATIFS.get(pays)

        if len(prenom) < 2:
            raise ValueError("Le prénom est nécessaire.")
        if not indicatif or not 7 <= len(numero_national) <= 15:
            raise ValueError("Le numéro WhatsApp est invalide.")
        if not _bool(data, "consentement_diagnostic"):
            raise ValueError(
                "Confirmez que nous pouvons utiliser ce numéro pour votre diagnostic."
            )

        domaine = _required_choice(data, "domaine", DiagnosticReponse.DOMAINES)
        experience = _required_choice(data, "experience", DiagnosticReponse.EXPERIENCE)
        situation = _required_choice(data, "situation", DiagnosticReponse.SITUATIONS)
        sollicitation = _required_choice(data, "sollicitation", DiagnosticReponse.SOLLICITATIONS)
        motivation = _required_choice(data, "motivation", DiagnosticReponse.MOTIVATIONS)

        domaine_autre = _text(data, "domaine_autre", 150)
        situation_autre = _text(data, "situation_autre", 150)
        motivation_autre = _text(data, "motivation_autre", 200)
        if domaine == "autre" and not domaine_autre:
            raise ValueError("Précisez votre domaine.")
        if situation == "autre" and not situation_autre:
            raise ValueError("Précisez votre situation.")
        if motivation == "autre" and not motivation_autre:
            raise ValueError("Précisez votre motivation.")

        difficulte = ""
        difficulte_consultant = ""
        anciennete_consultant = ""
        if situation == "consultant":
            anciennete_consultant = _required_choice(
                data, "anciennete_consultant", DiagnosticReponse.ANCIENNETE_CONSULTANT
            )
            difficulte_consultant = _required_choice(
                data, "difficulte", DiagnosticReponse.DIFFICULTES_CONSULTANT
            )
        else:
            difficulte = _required_choice(data, "difficulte", DiagnosticReponse.DIFFICULTES)

        difficulte_autre = _text(data, "difficulte_autre", 250)
        if (difficulte == "autre" or difficulte_consultant == "autre") and not difficulte_autre:
            raise ValueError("Précisez votre difficulté.")

        elements = data.get("elements", [])
        if not isinstance(elements, list):
            raise ValueError("Les éléments déjà définis sont invalides.")
        axes = {"positionnement", "offre", "tarifs", "prospection"}
        if not elements or not set(elements).issubset(axes | {"aucun"}):
            raise ValueError("Sélectionnez les éléments déjà définis.")
        if "aucun" in elements and len(elements) > 1:
            raise ValueError("« Aucun » ne peut pas être combiné avec un autre choix.")

        email = _text(data, "email", 254)
        duree = data.get("duree_secondes")
        duree = int(duree) if str(duree).isdigit() else None
        if duree is not None:
            duree = min(duree, 86400)

        reponse = DiagnosticReponse(
            session_id=_uuid(data.get("session_id")),
            prenom=prenom,
            pays=pays,
            indicatif=indicatif,
            numero_national=numero_national,
            whatsapp=f"{indicatif}{numero_national}",
            email=email,
            domaine=domaine,
            domaine_autre=domaine_autre,
            experience=experience,
            situation=situation,
            situation_autre=situation_autre,
            sollicitation=sollicitation,
            motivation=motivation,
            motivation_autre=motivation_autre,
            a_positionnement="positionnement" in elements,
            a_offre="offre" in elements,
            a_tarifs="tarifs" in elements,
            a_prospection="prospection" in elements,
            difficulte=difficulte,
            difficulte_autre=difficulte_autre if difficulte == "autre" else "",
            anciennete_consultant=anciennete_consultant,
            difficulte_consultant=difficulte_consultant,
            difficulte_consultant_autre=(
                difficulte_autre if difficulte_consultant == "autre" else ""
            ),
            duree_secondes=duree,
            utm_source=_text(data, "utm_source", 50),
            utm_medium=_text(data, "utm_medium", 50),
            utm_campaign=_text(data, "utm_campaign", 100),
            utm_content=_text(data, "utm_content", 100),
            utm_term=_text(data, "utm_term", 100),
            gclid=_text(data, "gclid", 255),
            device=_text(data, "device", 20),
            landing_path=_text(data, "landing_path", 255),
            referrer=_text(data, "referrer", 500),
            consentement_diagnostic=True,
            consentement_marketing=_bool(data, "consentement_marketing"),
        )
        reponse.calculer_score()
        domaine_affiche = (
            reponse.domaine_autre
            if reponse.domaine == "autre" and reponse.domaine_autre
            else reponse.get_domaine_display()
        )
        reponse.segment = analyse_pour(reponse, domaine_affiche)["segment"]
        reponse.full_clean()
        reponse.save()

        try:
            EbookAchat = apps.get_model("ebook", "EbookAchat")
            achat = EbookAchat.objects.filter(
                diagnostic_session_id=reponse.session_id, statut="paye"
            ).first()
            if achat:
                achat.diagnostic = reponse
                achat.save(update_fields=["diagnostic"])
                reponse.ebook_achete = True
                reponse.save(update_fields=["ebook_achete"])
        except (LookupError, AttributeError):
            pass

        DiagnosticEvenement.objects.filter(
            session_id=reponse.session_id, reponse__isnull=True
        ).update(reponse=reponse)
        DiagnosticEvenement.objects.get_or_create(
            session_id=reponse.session_id,
            reponse=reponse,
            nom="complete",
            ecran="contact",
            defaults={
                "meta": {
                    "score": reponse.score,
                    "situation": reponse.situation,
                    "segment": reponse.segment,
                }
            },
        )

        return JsonResponse(
            {
                "success": True,
                "redirect": reverse("diagnostic:resultat", args=[reponse.public_id]),
            }
        )
    except ValueError as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)
    except Exception:
        return JsonResponse(
            {"success": False, "error": "Une erreur est survenue. Réessayez."}, status=400
        )


@csrf_exempt
@require_POST
def evenement(request):
    """Télémétrie sans PII, compatible avec navigator.sendBeacon."""
    try:
        if not _same_origin(request):
            return JsonResponse({"success": False, "error": "Origine refusée."}, status=403)
        data = _json(request)
        session_id = _uuid(data.get("session_id"))
        nom = _text(data, "nom", 32)
        autorises = _choice_values(DiagnosticEvenement.EVENEMENTS) - {
            "complete",
            "purchase",
        }
        if nom not in autorises:
            raise ValueError("Événement invalide.")

        etape = data.get("etape")
        etape = int(etape) if str(etape).isdigit() else None
        if etape is not None and not 0 <= etape <= 20:
            etape = None
        duree = data.get("duree_ms")
        duree = int(duree) if str(duree).isdigit() else None
        if duree is not None:
            duree = min(duree, 3600000)

        ecran = _text(data, "ecran", 32)
        ecrans_autorises = {
            "intro",
            "ebook",
            "domaine",
            "experience",
            "situation",
            "anciennete",
            "sollicitation",
            "motivation",
            "elements",
            "difficulte",
            "contact",
            "resultat",
            "checkout",
            "merci",
        }
        if ecran not in ecrans_autorises:
            ecran = ""

        if DiagnosticEvenement.objects.filter(session_id=session_id).count() >= 100:
            return JsonResponse({"success": True, "limited": True}, status=202)

        reponse = DiagnosticReponse.objects.filter(session_id=session_id).first()
        defaults = {
            "reponse": reponse,
            "etape": etape,
            "duree_ms": duree,
            "meta": {
                "source": _text(data, "utm_source", 50) or _text(data, "source", 50),
                "medium": _text(data, "utm_medium", 50),
                "campaign": _text(data, "utm_campaign", 100),
                "content": _text(data, "utm_content", 100),
                "term": _text(data, "utm_term", 100),
                "device": _text(data, "device", 20),
                "path": _text(data, "landing_path", 255),
                "referrer": _text(data, "referrer", 500),
                "client_timestamp": _text(data, "client_timestamp", 40),
            },
        }
        uniques = {
            "view",
            "start",
            "step_view",
            "step_complete",
            "abandon",
            "result_view",
            "ebook_click",
            "checkout_view",
            "payment_started",
            "whatsapp_click",
        }
        if nom in uniques:
            _, created = DiagnosticEvenement.objects.get_or_create(
                session_id=session_id,
                nom=nom,
                ecran=ecran,
                defaults=defaults,
            )
            return JsonResponse({"success": True, "created": created})
        DiagnosticEvenement.objects.create(
            session_id=session_id,
            reponse=reponse,
            nom=nom,
            etape=etape,
            ecran=ecran,
            duree_ms=duree,
            meta=defaults["meta"],
        )
        return JsonResponse({"success": True})
    except ValueError as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)


@require_GET
@ensure_csrf_cookie
def resultat(request, public_id):
    reponse = get_object_or_404(DiagnosticReponse, public_id=public_id)
    domaine = (
        reponse.domaine_autre
        if reponse.domaine == "autre" and reponse.domaine_autre
        else reponse.get_domaine_display()
    )

    analyse = analyse_pour(reponse, domaine)
    if reponse.segment != analyse["segment"]:
        reponse.segment = analyse["segment"]
        reponse.save(update_fields=["segment"])

    DiagnosticEvenement.objects.get_or_create(
        session_id=reponse.session_id,
        reponse=reponse,
        nom="result_view",
        ecran="resultat",
    )
    config = _config()
    config["ebook_url"] = _add_query(
        config["ebook_url"],
        diagnostic=reponse.public_id,
        utm_source="diagnostic",
        utm_medium="owned",
        utm_campaign="ebook_launch",
        utm_content=reponse.segment,
    )
    return render(
        request,
        "diagnostic/resultat.html",
        {
            "r": reponse,
            "titre": analyse["titre"],
            "intro": analyse["intro"],
            "phase": analyse["phase"],
            "domaine": domaine,
            "contenu": contenu_pour(reponse),
            "analyse": analyse,
            **config,
        },
    )


@require_POST
def enregistrer_avis(request, public_id):
    try:
        data = _json(request)
        note = int(data.get("note", 0))
        if note not in range(1, 6):
            raise ValueError("Choisissez une note de 1 à 5.")
        reponse = get_object_or_404(DiagnosticReponse, public_id=public_id)
        reponse.note_formulaire = note
        reponse.commentaire_formulaire = _text(data, "commentaire", 1000)
        reponse.date_feedback = timezone.now()
        reponse.save(
            update_fields=["note_formulaire", "commentaire_formulaire", "date_feedback"]
        )
        return JsonResponse({"success": True})
    except ValueError as exc:
        return JsonResponse({"success": False, "error": str(exc)}, status=400)
