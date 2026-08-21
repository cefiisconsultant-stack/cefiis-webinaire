from django.conf import settings


# Compatibilité avec les fichiers qui importent encore PRIX_EBOOK.
# La valeur réelle provient uniquement du fichier .env.
PRIX_EBOOK = settings.EBOOK_PRICE