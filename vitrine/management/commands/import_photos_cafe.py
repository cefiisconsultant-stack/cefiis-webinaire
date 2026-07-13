import os
from django.core.management.base import BaseCommand
from django.core.files import File
from vitrine.models import EvenementPhoto

# Numéros des photos à importer, dans l'ordre d'affichage souhaité
NUMEROS = ["38", "39", "40", "50", "51", "18", "31", "36", "37", "06", "08", "12"]

SOURCE_DIR = os.path.expanduser("~/PHOTOS_renamed")


class Command(BaseCommand):
    help = "Importe les photos du Café des Consultants depuis ~/PHOTOS_renamed vers EvenementPhoto"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source", type=str, default=SOURCE_DIR,
            help="Dossier contenant les photos numérotées (défaut: ~/PHOTOS_renamed)",
        )
        parser.add_argument(
            "--clear", action="store_true",
            help="Supprime les EvenementPhoto existantes avant l'import",
        )

    def handle(self, *args, **options):
        source = options["source"]

        if options["clear"]:
            deleted, _ = EvenementPhoto.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"{deleted} ancienne(s) photo(s) supprimée(s)."))

        if not os.path.isdir(source):
            self.stderr.write(self.style.ERROR(f"Dossier introuvable : {source}"))
            return

        importees = 0
        for i, numero in enumerate(NUMEROS, start=1):
            chemin = os.path.join(source, f"{numero}.jpg")
            if not os.path.exists(chemin):
                self.stderr.write(self.style.WARNING(f"Introuvable, ignoré : {chemin}"))
                continue

            with open(chemin, "rb") as f:
                photo = EvenementPhoto(
                    evenement="Café des Consultants",
                    order=i,
                    legende="",
                )
                photo.image.save(f"cafe_{numero}.jpg", File(f), save=True)

            importees += 1
            self.stdout.write(self.style.SUCCESS(f"✅ {numero}.jpg importée (ordre {i})"))

        self.stdout.write(self.style.SUCCESS(f"\nTerminé : {importees} photo(s) importée(s) sur {len(NUMEROS)}."))