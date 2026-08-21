import uuid

from django.db import models


class EbookAchat(models.Model):
    STATUT_CHOICES = [
        ("en_attente", "En attente"),
        ("paye", "Payé"),
        ("echec", "Échec"),
    ]
    email = models.EmailField()
    prenom = models.CharField(max_length=100, blank=True, default="")
    transaction_id = models.CharField(max_length=120, unique=True)
    montant = models.PositiveIntegerField(default=2000)  # en FCFA
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    token_telechargement = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    email_envoye = models.BooleanField(default=False)
    nombre_telechargements = models.PositiveSmallIntegerField(default=0)
    expiration_telechargement = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
    )
    dernier_telechargement_at = models.DateTimeField(null=True, blank=True)
    diagnostic = models.ForeignKey(
        "diagnostic.DiagnosticReponse",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="achats_ebook",
    )
    diagnostic_session_id = models.UUIDField(null=True, blank=True, db_index=True)

    def __str__(self):
        return f"{self.email} - {self.statut} - {self.transaction_id}"


class EbookTelechargementEvenement(models.Model):
    class Resultat(models.TextChoices):
        AUTORISE = "autorise", "Autorisé"
        EXPIRE = "expire", "Lien expiré"
        LIMITE = "limite", "Limite atteinte"
        FICHIER_ABSENT = "fichier_absent", "Fichier absent"

    achat = models.ForeignKey(
        EbookAchat,
        on_delete=models.CASCADE,
        related_name="evenements_telechargement",
    )
    resultat = models.CharField(max_length=20, choices=Resultat.choices)
    compteur_apres = models.PositiveSmallIntegerField(default=0)
    empreinte_ip = models.CharField(max_length=64, blank=True, default="")
    user_agent = models.CharField(max_length=255, blank=True, default="")
    date_creation = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ("-date_creation",)
        verbose_name = "événement de téléchargement"
        verbose_name_plural = "événements de téléchargement"

    def __str__(self):
        return f"{self.achat.email} - {self.get_resultat_display()}"
