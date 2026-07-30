from django.core.management.base import BaseCommand
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from webinaire.models import ReservationWebinaire


class Command(BaseCommand):
    help = "Envoie le rappel J-2 avant le webinaire"

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email unique pour test')
        parser.add_argument('--exclus', nargs='+', default=[], help='Emails a exclure')
        parser.add_argument('--sujet', type=str,
                            default="Dans 2 jours : ce qui separe un expert d'un consultant paye")

    def handle(self, *args, **options):
        if options.get('email'):
            inscrits = ReservationWebinaire.objects.filter(email=options['email'])
        else:
            inscrits = ReservationWebinaire.objects.exclude(email__in=options.get('exclus', []))

        envoyes = 0
        for inscrit in inscrits:
            html = render_to_string('webinaire/rappel_webinaire-j2.html', {'inscrit': inscrit})
            msg = EmailMultiAlternatives(
                subject=options['sujet'],
                body=strip_tags(html),
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[inscrit.email],
            )
            msg.attach_alternative(html, "text/html")
            try:
                msg.send(fail_silently=False)
                self.stdout.write(f"OK  {inscrit.email}")
                envoyes += 1
            except Exception as e:
                self.stdout.write(f"ERR {inscrit.email} : {e}")

        self.stdout.write(f"--- {envoyes} emails envoyes ---")
