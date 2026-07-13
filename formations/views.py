from django.shortcuts import render
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from urllib.parse import quote
from .models import Offer, EbookPopup, InscriptionLead


def offres(request):
    parcours = Offer.objects.filter(is_active=True, categorie="parcours").order_by("order")
    catalogue = Offer.objects.filter(is_active=True, categorie="catalogue").order_by("order")
    popup, _ = EbookPopup.objects.get_or_create(pk=1)
    return render(request, "formations/offres.html", {
        "parcours": parcours,
        "catalogue": catalogue,
        "popup": popup if popup.is_active else None,
    })



WHATSAPP_NUMERO = "22997345232"


@csrf_exempt
@require_POST
def creer_lead(request):
    try:
        data = json.loads(request.body.decode("utf-8"))
        offer = Offer.objects.filter(id=data.get("offer_id")).first()

        lead = InscriptionLead.objects.create(
            offer=offer,
            nom=data.get("nom", "").strip(),
            prenom=data.get("prenom", "").strip(),
            profession=data.get("profession", "").strip(),
            diplome=data.get("diplome", "").strip(),
        )

        message = (
            f"Bonjour Cefiis-IDH 👋 Je m'appelle {lead.prenom} {lead.nom}, "
            f"je suis intéressé(e) par la formation « {offer.title if offer else ''} ». "
            f"Pouvez-vous me communiquer la prochaine date de démarrage et les modalités d'inscription ? Merci !"
        )
        whatsapp_url = f"https://wa.me/{WHATSAPP_NUMERO}?text={quote(message)}"

        return JsonResponse({"success": True, "whatsapp_url": whatsapp_url})

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=400)