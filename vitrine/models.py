from django.db import models


class PortfolioItem(models.Model):
    """Réalisations de la Maison du Consultant à mettre en avant."""
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to="portfolio/", blank=True, null=True)
    lien = models.URLField(blank=True, help_text="Optionnel — lien vers le détail")
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.title


class EvenementPhoto(models.Model):
    """Galerie du Café des Consultants (et futurs événements)."""
    evenement = models.CharField(max_length=150, default="Café des Consultants")
    image = models.ImageField(upload_to="evenements/")
    legende = models.CharField(max_length=200, blank=True)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.evenement} — {self.legende or self.pk}"


class Realisation(models.Model):
    """Études de marché / missions réalisées."""
    titre = models.CharField(max_length=150)
    secteur = models.CharField(max_length=120, blank=True, help_text="Ex: Agroalimentaire, IoT, Formation...")
    description = models.TextField()
    resultat = models.CharField(max_length=200, blank=True, help_text="Ex: '+30% de conversion en 3 mois'")
    image = models.ImageField(upload_to="realisations/", blank=True, null=True)
    order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.titre

class RealisationImage(models.Model):
    realisation = models.ForeignKey(Realisation, related_name="images", on_delete=models.CASCADE)
    image = models.ImageField(upload_to="realisations/galerie/")
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"Image {self.order} — {self.realisation.titre}"