from django.contrib import admin
from .models import Article, Categorie


@admin.register(Categorie)
class CategorieAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("nom",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("titre", "categorie", "date_publication", "is_active")
    list_editable = ("is_active",)
    list_filter = ("categorie", "is_active")
    prepopulated_fields = {"slug": ("titre",)}
    ordering = ("-date_publication",)