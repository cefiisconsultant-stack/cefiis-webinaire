from django.contrib import admin
from .models import PortfolioItem, EvenementPhoto, Realisation, RealisationImage


class RealisationImageInline(admin.TabularInline):
    model = RealisationImage
    extra = 3


@admin.register(PortfolioItem)
class PortfolioItemAdmin(admin.ModelAdmin):
    list_display = ("order", "title", "is_active")
    list_editable = ("is_active",)
    ordering = ("order",)


@admin.register(EvenementPhoto)
class EvenementPhotoAdmin(admin.ModelAdmin):
    list_display = ("order", "evenement", "legende", "is_active")
    list_editable = ("is_active",)
    list_filter = ("evenement",)
    ordering = ("order",)


@admin.register(Realisation)
class RealisationAdmin(admin.ModelAdmin):
    list_display = ("order", "titre", "secteur", "resultat", "is_active")
    list_editable = ("is_active",)
    ordering = ("order",)
    inlines = [RealisationImageInline]

