from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from webinaire.models import ReservationWebinaire


class Command(BaseCommand):
    help = 'Envoie l\'email de suivi aux inscrits absents du webinaire'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email unique pour test')
        parser.add_argument(
            '--exclus',
            nargs='+',
            default=[],
            help='Emails à exclure (présents + nouveaux)'
        )

    def handle(self, *args, **options):
        exclus = options.get('exclus', [])

        if options.get('email'):
            inscrits = ReservationWebinaire.objects.filter(email=options['email'])
        else:
            inscrits = ReservationWebinaire.objects.exclude(email__in=exclus)

        envoyes = 0
        for inscrit in inscrits:
            html = render_to_string('webinaire/email_absent_webinaire.html', {'inscrit': inscrit})
            text = strip_tags(html)
            msg = EmailMultiAlternatives(
                subject="On aurait aimé vous avoir avec nous samedi 🎙️",
                body=text,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[inscrit.email],
            )
            msg.attach_alternative(html, "text/html")
            try:
                msg.send(fail_silently=False)
                self.stdout.write(f"✅ Envoyé à {inscrit.email}")
                envoyes += 1
            except Exception as e:
                self.stdout.write(f"❌ Erreur pour {inscrit.email} : {e}")

        self.stdout.write(f"--- {envoyes} emails envoyés ---")
