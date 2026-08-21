from datetime import timedelta

from django.contrib import admin
from django.conf import settings
from django.utils import timezone

from .models import EbookAchat, EbookTelechargementEvenement


class EbookTelechargementEvenementInline(admin.TabularInline):
    model = EbookTelechargementEvenement
    extra = 0
    can_delete = False
    fields = (
        "date_creation",
        "resultat",
        "compteur_apres",
        "empreinte_ip",
        "user_agent",
    )
    readonly_fields = fields

    def has_add_permission(self, request, obj=None):
        return False


@admin.action(description="Réactiver le lien de téléchargement sélectionné")
def reactiver_liens_telechargement(modeladmin, request, queryset):
    expiration = timezone.now() + timedelta(
        hours=max(1, int(settings.EBOOK_DOWNLOAD_EXPIRY_HOURS))
    )
    updated = queryset.filter(statut="paye").update(
        nombre_telechargements=0,
        expiration_telechargement=expiration,
        dernier_telechargement_at=None,
    )
    modeladmin.message_user(
        request,
        f"{updated} lien(s) réactivé(s).",
    )

@admin.register(EbookAchat)
class EbookAchatAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "prenom",
        "montant",
        "statut",
        "nombre_telechargements",
        "expiration_telechargement",
        "dernier_telechargement_at",
        "date_paiement",
        "email_envoye",
    )
    list_filter = ("statut", "email_envoye")
    search_fields = ("email", "transaction_id", "diagnostic__prenom", "diagnostic__whatsapp")
    readonly_fields = (
        "token_telechargement",
        "diagnostic",
        "diagnostic_session_id",
        "nombre_telechargements",
        "expiration_telechargement",
        "dernier_telechargement_at",
    )
    actions = (reactiver_liens_telechargement,)
    inlines = (EbookTelechargementEvenementInline,)


@admin.register(EbookTelechargementEvenement)
class EbookTelechargementEvenementAdmin(admin.ModelAdmin):
    list_display = (
        "achat",
        "resultat",
        "compteur_apres",
        "date_creation",
    )
    list_filter = ("resultat", "date_creation")
    search_fields = ("achat__email", "achat__transaction_id")
    readonly_fields = (
        "achat",
        "resultat",
        "compteur_apres",
        "empreinte_ip",
        "user_agent",
        "date_creation",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
