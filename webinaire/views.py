from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import *
import threading
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.utils.html import escape
from django.http import HttpResponse
from django.shortcuts import redirect
from django.utils import timezone



def webinaire_pre_frame_bridge(request):
    return render(request, 'webinaire/webinaire-pre-frame-bridge-1.html')

def webinaire_page(request):
    return render(request, 'webinaire/webinaire-reservation-page.html')

def webinaire_confirmation(request):
    return render(request, 'webinaire/webinaire-confirmation-page.html')


def send_webinaire_confirmation_email(reservation):
    """Envoie l'email de confirmation d'inscription au webinaire"""
    try:
        # Construire un nom complet propre
        if reservation.nom and reservation.nom != "Anonyme":
            full_name = f"{reservation.prenom} {reservation.nom}"
        else:
            full_name = reservation.prenom

        html_content = render_to_string("webinaire/email_inscription_webinaire.html", {
            "full_name": full_name,
            "profession": reservation.profession if reservation.profession else "",
            "site_name": "Cefiis-IDH",  # ou votre nom
            "year": datetime.now().year,
        })

        subject = "✅ Votre place est réservée – Webinaire Consultant Indépendant"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_email = [reservation.email]

        msg = EmailMultiAlternatives(subject, "", from_email, to_email)
        msg.attach_alternative(html_content, "text/html")
        msg.send()

        print(f"[OK] Email envoyé à {reservation.email}")

    except Exception as e:
        print(f"[ERREUR] Impossible d’envoyer l’email à {reservation.email} : {e}")


@csrf_exempt
def reservation_webinaire(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body.decode("utf-8"))
            
            # Récupération des données
            email = data.get("email", "").strip()
            prenom = escape(data.get("prenom", "").strip())
            # Ces champs ne sont plus obligatoires
            nom = escape(data.get("nom", "").strip()) or "Anonyme"
            profession = escape(data.get("profession", "").strip()) or ""
            niveau_etude = escape(data.get("niveau_etude", "").strip()) or "Non spécifié"
            
            # Validation de l'email
            try:
                validate_email(email)
            except ValidationError:
                return JsonResponse({
                    "success": False, 
                    "error": "Veuillez fournir une adresse email valide.",
                    "field_errors": {"email": "Adresse email invalide"}
                }, status=400)
            
            # Validation des champs obligatoires (seulement prénom)
            field_errors = {}
            if not prenom:
                field_errors["prenom"] = "Ce champ est obligatoire"
            # Plus de validation pour nom, profession, niveau_etude
            
            if field_errors:
                return JsonResponse({
                    "success": False, 
                    "error": "Veuillez corriger les erreurs dans le formulaire.",
                    "field_errors": field_errors
                }, status=400)
            
            # Vérifier si l'email existe déjà
            if ReservationWebinaire.objects.filter(email=email).exists():
                return JsonResponse({
                    "success": False, 
                    "error": "Cet email est déjà inscrit à notre webinaire.",
                    "field_errors": {"email": "Cet email est déjà inscrit"}
                }, status=400)
            
            # Créer la nouvelle réservation avec les champs par défaut si absents
            reservation = ReservationWebinaire.objects.create(
                email=email,
                prenom=prenom,
                nom=nom,
                profession=profession,
                niveau_etude=niveau_etude
            )
            
            message = "Nouvelle réservation enregistrée."
            threading.Thread(target=send_webinaire_confirmation_email, args=(reservation,)).start()
            print(message)

            return JsonResponse(
                {"success": True, "id": reservation.id, "message": message},
                status=200
            )

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=400)

    return JsonResponse({"error": "Méthode non autorisée"}, status=405)

def webinaire_page_c(request):
    return render(request, 'webinaire/inscription-webinaire-c.html')

# def email_open(request):
#     email = request.GET.get("email")
#     email_name = request.GET.get("name", "unknown")

#     obj, created = EmailTracking.objects.get_or_create(email=email, email_name=email_name)
#     obj.opened = True
#     obj.open_count += 1
#     obj.last_opened_at = timezone.now()
#     obj.save()

#     # Pixel transparent 1x1
#     pixel = b'\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00' \
#             b'\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00' \
#             b'\x01\x00\x01\x00\x00\x02\x02D\x01\x00;'
#     return HttpResponse(pixel, content_type="image/gif")
