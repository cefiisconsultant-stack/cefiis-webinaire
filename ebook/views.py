import requests
from django.conf import settings
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, FileResponse, Http404
from django.core.mail import EmailMessage
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json, os

from .models import EbookAchat

PRIX_EBOOK = 2000  # FCFA


def vente_ebook(request):
    return render(request, "ebook/vente_ebook.html", {
        "prix": PRIX_EBOOK,
        "kkiapay_public_key": settings.KKIAPAY_PUBLIC_KEY,
        "kkiapay_sandbox": settings.KKIAPAY_SANDBOX,
    })


@csrf_exempt
@require_POST
def verifier_paiement(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        transaction_id = data.get("transactionId")
        email = data.get("email", "").strip()
        prenom = data.get("prenom", "").strip()

        if not transaction_id or not email:
            return JsonResponse({"success": False, "error": "Données manquantes."}, status=400)

        resp = requests.post(
            "https://api.kkiapay.me/api/v1/transactions/status",
            json={"transactionId": transaction_id},
            headers={
                "x-api-key": settings.KKIAPAY_PUBLIC_KEY,
                "x-private-key": settings.KKIAPAY_PRIVATE_KEY,
            },
            timeout=15,
        )

        print("=== KKIAPAY VERIFY DEBUG ===")
        print("HTTP status:", resp.status_code)
        print("Response body:", resp.text)
        print("============================")

        result = resp.json()

        if result.get("status") != "SUCCESS":
            EbookAchat.objects.update_or_create(
                transaction_id=transaction_id,
                defaults={"email": email, "prenom": prenom, "statut": "echec"},
            )
            return JsonResponse({
                "success": False,
                "error": f"Paiement non confirmé (réponse Kkiapay : {result})."
            }, status=400)

        achat, _ = EbookAchat.objects.update_or_create(
            transaction_id=transaction_id,
            defaults={
                "email": email,
                "prenom": prenom,
                "montant": result.get("amount", PRIX_EBOOK),
                "statut": "paye",
                "date_paiement": timezone.now(),
            },
        )

        if not achat.email_envoye:
            envoyer_ebook_par_email(achat, request=request)
            achat.email_envoye = True
            achat.save(update_fields=["email_envoye"])

        return JsonResponse({"success": True, "redirect": f"/ebook/merci/{achat.token_telechargement}/"})

    except Exception as e:
        print("=== KKIAPAY VERIFY EXCEPTION ===", e)
        return JsonResponse({"success": False, "error": str(e)}, status=400)


def envoyer_ebook_par_email(achat, request=None):
    if request is not None:
        lien = request.build_absolute_uri(f"/ebook/telecharger/{achat.token_telechargement}/")
    else:
        lien = f"{settings.SITE_URL}/ebook/telecharger/{achat.token_telechargement}/"

    msg = EmailMessage(
        subject="Votre ebook — De l'Expert au Consultant Professionnel",
        body=f"Bonjour {achat.prenom or ''},\n\nMerci pour votre achat. Voici votre lien de téléchargement :\n{lien}\n\nBonne lecture,\nCefiis-IDH",
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[achat.email],
    )
    msg.send(fail_silently=True)


def page_merci(request, token):
    achat = get_object_or_404(EbookAchat, token_telechargement=token, statut="paye")
    return render(request, "ebook/merci.html", {"achat": achat})


def telecharger_ebook(request, token):
    achat = get_object_or_404(EbookAchat, token_telechargement=token, statut="paye")
    chemin = os.path.join(settings.MEDIA_ROOT, "ebook", "De_l_Expert_au_Consultant_Professionnel.pdf")
    if not os.path.exists(chemin):
        raise Http404("Fichier introuvable.")
    return FileResponse(open(chemin, "rb"), as_attachment=True, filename="De_l_Expert_au_Consultant_Professionnel.pdf")