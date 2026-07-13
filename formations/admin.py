from django.contrib import admin
from .models import Offer, EbookPopup, InscriptionLead


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("categorie", "order", "title", "type_offre", "price_fcfa", "is_active")
    list_editable = ("is_active",)
    list_filter = ("categorie", "type_offre")
    ordering = ("categorie", "order")
    fields = ("categorie", "type_offre", "order", "title", "subtitle", "audience_label",
              "description", "livrables", "prerequis", "duration_label",
              "price_fcfa", "price_barre_override", "lien_inscription", "is_active")

@admin.register(EbookPopup)
class EbookPopupAdmin(admin.ModelAdmin):
    list_display = ("title", "price_fcfa", "is_active", "delay_seconds")

    def has_add_permission(self, request):
        return not EbookPopup.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
    
@admin.register(InscriptionLead)
class InscriptionLeadAdmin(admin.ModelAdmin):
    list_display = ("date_creation", "nom", "prenom", "profession", "offer")
    list_filter = ("offer",)
    ordering = ("-date_creation",)