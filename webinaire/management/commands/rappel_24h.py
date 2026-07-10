from django.core.management.base import BaseCommand
from webinaire.utils import envoyer_rappel_24h

class Command(BaseCommand):
    help = 'Envoie le rappel J-24 aux inscrits'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email unique pour test')

    def handle(self, *args, **options):
        envoyer_rappel_24h(email_test=options.get('email'))
