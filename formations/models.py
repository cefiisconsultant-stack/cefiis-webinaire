from django.db import models


class Offer(models.Model):
    CATEGORIE_CHOICES = [
        ("parcours", "Parcours professionnel (Initiation → Pro)"),
        ("catalogue", "Formation ou ressource complémentaire"),
    ]
    TYPE_CHOICES = [
        ("formation", "Formation"),
        ("document", "Modèle / Document à télécharger"),
    ]

    categorie = models.CharField(max_length=20, choices=CATEGORIE_CHOICES, default="parcours")
    type_offre = models.CharField(max_length=20, choices=TYPE_CHOICES, default="formation")
    order = models.PositiveIntegerField(default=1, help_text="Parcours: 1=Initiation, 2=Avancée, 3=Pro. Catalogue: ordre d'affichage libre.")
    title = models.CharField(max_length=150)
    subtitle = models.CharField(max_length=200, blank=True)
    description = models.TextField()
    audience_label = models.CharField(max_length=120, blank=True)
    livrables = models.TextField(blank=True, help_text="Un livrable par ligne — ignoré pour les documents.")
    prerequis = models.CharField(max_length=150, blank=True)
    price_fcfa = models.PositiveIntegerField()
    price_barre_override = models.PositiveIntegerField(
        null=True, blank=True,
        help_text="Prix barré personnalisé. Laisser vide pour calcul automatique (x3 du prix actuel)."
    )
    duration_label = models.CharField(max_length=80, blank=True)
    lien_inscription = models.URLField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["categorie", "order"]

    def get_livrables_list(self):
        return [l.strip() for l in self.livrables.splitlines() if l.strip()]

    @property
    def price_barre_fcfa(self):
        return self.price_barre_override or self.price_fcfa * 3

    @property
    def discount_percent(self):
        barre = self.price_barre_fcfa
        if not barre or barre <= self.price_fcfa:
            return 0
        return round((1 - self.price_fcfa / barre) * 100)

    def __str__(self):
        return f"[{self.get_categorie_display()}] {self.title} — {self.price_fcfa} FCFA"


class EbookPopup(models.Model):
    """Singleton : une seule configuration pour le pop-up ebook."""
    title = models.CharField(max_length=150, default="De l'Expert au Consultant Professionnel")
    pitch = models.TextField(default="Le guide en 5 étapes pour transformer votre expertise en activité de conseil rentable.")
    price_fcfa = models.PositiveIntegerField(default=2000)
    lien_ebook = models.URLField(default="https://ebook.cefiis.com")
    is_active = models.BooleanField(default=True)
    delay_seconds = models.PositiveIntegerField(default=8, help_text="Délai avant apparition du pop-up (secondes)")

    def __str__(self):
        return "Configuration pop-up ebook"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

class InscriptionLead(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.SET_NULL, null=True, related_name="leads")
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    profession = models.CharField(max_length=150, blank=True)
    diplome = models.CharField(max_length=150, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date_creation"]

    def __str__(self):
        return f"{self.prenom} {self.nom} — {self.offer.title if self.offer else 'formation supprimée'}"