from django.db import models
from django.urls import reverse


class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.nom


class Article(models.Model):
    titre = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=220)
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles")
    extrait = models.CharField(max_length=280, help_text="Résumé affiché sur la liste des articles (1-2 phrases).")
    contenu = models.TextField(help_text="Corps de l'article. Une ligne vide = un nouveau paragraphe.")
    image = models.ImageField(upload_to="blog/", blank=True, null=True)
    auteur = models.CharField(max_length=100, default="Cefiis-IDH")
    temps_lecture = models.CharField(max_length=20, blank=True, help_text="Ex: '5 min'")
    date_publication = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-date_publication"]

    def __str__(self):
        return self.titre

    def get_absolute_url(self):
        return reverse("blog_detail", kwargs={"slug": self.slug})

    def get_paragraphes(self):
        return [p.strip() for p in self.contenu.split("\n\n") if p.strip()]