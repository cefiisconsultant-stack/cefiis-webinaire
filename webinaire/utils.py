# webinaire/utils.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from webinaire.models import *
from django.conf import settings


def envoyer_rappel_webinaire_cibles():
    # Liste des emails valides qui n'ont pas encore reçu
    emails_cibles = ReservationWebinaire.objects.filter(
        niveau_sequence__lte=2
    ).values_list("email", flat=True).distinct()


    for email_dest in emails_cibles:
        subject = "[Enfin] Le Webinaire à commencé - Ne manquez pas !"
        # subject = "[Rappel] Votre webinaire démarre dans 5 Heures !"
        # subject =  "⏰ N’oubliez pas : votre webinaire a lieu demain !" 
        
        
        # On peut passer un "fake inscrit" minimal juste pour le template
        context = {"inscrit": {"prenom": "Cher participant", "email": email_dest}}
        
        # Version HTML
        html_content = render_to_string("webinaire/envoie_identifiant_connexion.html", context)
        # html_content = render_to_string("webinaire/rappel_webinaire-1.html", context) 
        
        # Version texte brut
        text_content = strip_tags(html_content)

        email = EmailMultiAlternatives(
            subject,
            text_content,
            "Cefiis-IDH <cefiis.consultant@gmail.com>",  # expéditeur
            [email_dest]  # destinataire
        )
        email.attach_alternative(html_content, "text/html")
        email.send()
        print(f"✅ Email envoyé avec succès à {email_dest}")
    
    print("🚀 Tous les emails ciblés ont été envoyés !")



def send_soap_opera_email1_to_all():
    """Envoie le premier Email de la Soap Opera Sequence à tous les inscrits"""

    reservations = ReservationWebinaire.objects.filter(
        dans_sequence_opera=False
    )

    for reservation in reservations:
        try:
            html_content = render_to_string("webinaire/email_soap_opera_sequence_1.html", {
                "prenom": reservation.prenom,
                "nom": reservation.nom,
                "reservation": reservation,
            })

            subject = "Le secret qui a changé ma vie de consultant"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [reservation.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            print(f"[OK] Email 1 envoyé à {reservation.email}")

            # ✅ Mettre à jour le suivi de la séquence
            reservation.dans_sequence_opera = True
            reservation.niveau_sequence = 1
            reservation.save(update_fields=["dans_sequence_opera", "niveau_sequence"])

        except Exception as e:
            print(f"[ERREUR] Email 1 non envoyé à {reservation.email} : {e}")



def send_soap_opera_email2_to_all():
    """Envoie le 2e Email de la Soap Opera Sequence à ceux qui ont reçu le premier"""

    reservations = ReservationWebinaire.objects.filter(
        dans_sequence_opera=True,
        niveau_sequence=1
    )

    for reservation in reservations:
        try:
            html_content = render_to_string("webinaire/email_soap_opera_sequence_2.1.html", {
                "prenom": reservation.prenom,
                "nom": reservation.nom,
                "reservation": reservation,
            })

            subject = " 🔑 Le secret que 12 ans d’attente m’ont appris"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [reservation.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            print(f"[OK] Email 2 envoyé à {reservation.email}")

            # ✅ Mettre à jour le suivi de la séquence
            reservation.niveau_sequence = 2
            reservation.save(update_fields=["niveau_sequence"])

        except Exception as e:
            print(f"[ERREUR] Email 2 non envoyé à {reservation.email} : {e}")


def send_soap_opera_email3_to_all():

    reservations = ReservationWebinaire.objects.filter(
        dans_sequence_opera=True,
        niveau_sequence=2
    )

    for reservation in reservations:
        try:
            html_content = render_to_string("webinaire/email_soap_opera_sequence_3.html", {
                "prenom": reservation.prenom,
                "nom": reservation.nom,
                "reservation": reservation,
            })

            subject = "7 bénéfices insoupçonnés de la vie du consultant"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [reservation.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            print(f"[OK] Email 2 envoyé à {reservation.email}")

            # ✅ Mettre à jour le suivi de la séquence
            reservation.niveau_sequence = 3
            reservation.save(update_fields=["niveau_sequence"])

        except Exception as e:
            print(f"[ERREUR] Email 2 non envoyé à {reservation.email} : {e}")

def send_soap_opera_email4_to_all():

    reservations = ReservationWebinaire.objects.filter(
        dans_sequence_opera=True,
        niveau_sequence=3
    )

    for reservation in reservations:
        try:
            html_content = render_to_string("webinaire/email_soap_opera_sequence_4.html", {
                "prenom": reservation.prenom,
                "nom": reservation.nom,
                "reservation": reservation,
            })

            subject = " 🔥 Je t'offre une réduction de 90% - ⏰ plus que 2 places restantes"
            from_email = settings.DEFAULT_FROM_EMAIL
            to_email = [reservation.email]

            msg = EmailMultiAlternatives(subject, "", from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            print(f"[OK] Email 2 envoyé à {reservation.email}")

            # ✅ Mettre à jour le suivi de la séquence
            reservation.niveau_sequence = 4
            reservation.save(update_fields=["niveau_sequence"])

        except Exception as e:
            print(f"[ERREUR] Email 2 non envoyé à {reservation.email} : {e}")


