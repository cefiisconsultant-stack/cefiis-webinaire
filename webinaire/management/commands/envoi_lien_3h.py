from django.core.management.base import BaseCommand
from webinaire.utils import envoyer_lien_webinaire_3h

class Command(BaseCommand):
    help = 'Envoie l\'email contenant le lien du webinaire'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email unique pour test')
        parser.add_argument('--lien', type=str, default='https://meet.google.com/duo-zadk-mof')

    def handle(self, *args, **options):
        envoyer_lien_webinaire_3h(
            email_test=options.get('email'),
            lien_webinaire=options.get('lien')
        )
