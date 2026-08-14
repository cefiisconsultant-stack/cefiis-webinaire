from django.contrib import admin

from .models import DiagnosticEvenement, DiagnosticReponse


@admin.register(DiagnosticReponse)
class DiagnosticReponseAdmin(admin.ModelAdmin):
    list_display = (
        "prenom",
        "whatsapp",
        "domaine",
        "situation",
        "segment",
        "score",
        "difficulte_affichee",
        "note_formulaire",
        "contacte",
        "ebook_achete",
        "date_creation",
    )
    list_filter = (
        "situation",
        "segment",
        "domaine",
        "experience",
        "sollicitation",
        "motivation",
        "difficulte",
        "difficulte_consultant",
        "note_formulaire",
        "contacte",
        "ebook_achete",
        "utm_source",
        "utm_campaign",
        "utm_content",
        "device",
        "consentement_marketing",
        "date_creation",
    )
    list_editable = ("contacte", "ebook_achete")
    search_fields = (
        "prenom",
        "whatsapp",
        "email",
        "domaine_autre",
        "situation_autre",
        "difficulte_autre",
        "difficulte_consultant_autre",
    )
    readonly_fields = (
        "public_id",
        "session_id",
        "score",
        "segment",
        "utm_source",
        "utm_medium",
        "utm_campaign",
        "utm_content",
        "utm_term",
        "gclid",
        "date_creation",
        "date_feedback",
    )
    date_hierarchy = "date_creation"
    fieldsets = (
        ("Contact", {"fields": ("prenom", "pays", "indicatif", "numero_national", "whatsapp", "email")}),
        ("Profil", {"fields": ("domaine", "domaine_autre", "experience", "situation", "situation_autre", "sollicitation", "segment")}),
        ("Motivation", {"fields": ("motivation", "motivation_autre")}),
        ("Socle", {"fields": ("a_positionnement", "a_offre", "a_tarifs", "a_prospection", "score")}),
        ("Difficulté", {"fields": ("difficulte", "difficulte_autre")}),
        ("Branche consultant", {"classes": ("collapse",), "fields": ("anciennete_consultant", "difficulte_consultant", "difficulte_consultant_autre")}),
        ("Qualité du formulaire", {"fields": ("note_formulaire", "commentaire_formulaire", "date_feedback")}),
        ("Consentements", {"fields": ("consentement_diagnostic", "consentement_marketing")}),
        ("Suivi commercial", {"fields": ("contacte", "ebook_achete", "notes")}),
        ("Mesure", {"classes": ("collapse",), "fields": ("duree_secondes", "device", "landing_path", "referrer", "utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "gclid", "public_id", "session_id", "date_creation")}),
    )

    @admin.display(description="Difficulté")
    def difficulte_affichee(self, obj):
        return (
            obj.get_difficulte_consultant_display()
            if obj.est_consultant
            else obj.get_difficulte_display()
        )


@admin.register(DiagnosticEvenement)
class DiagnosticEvenementAdmin(admin.ModelAdmin):
    list_display = ("nom", "session_id", "reponse", "etape", "ecran", "duree_ms", "date_creation")
    list_filter = ("nom", "ecran", "date_creation")
    search_fields = ("session_id", "reponse__prenom", "reponse__whatsapp")
    readonly_fields = ("event_id", "session_id", "reponse", "nom", "etape", "ecran", "duree_ms", "meta", "date_creation")
    date_hierarchy = "date_creation"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
