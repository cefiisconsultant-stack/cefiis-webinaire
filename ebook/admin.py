from django.contrib import admin
from .models import EbookAchat

@admin.register(EbookAchat)
class EbookAchatAdmin(admin.ModelAdmin):
    list_display = ("email", "prenom", "montant", "statut", "date_creation", "date_paiement", "email_envoye")
    list_filter = ("statut", "email_envoye")
    search_fields = ("email", "transaction_id")