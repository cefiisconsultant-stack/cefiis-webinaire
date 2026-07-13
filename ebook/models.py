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
    montant = models.PositiveIntegerField(default=10000)  # en FCFA
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default="en_attente")
    token_telechargement = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_paiement = models.DateTimeField(null=True, blank=True)
    email_envoye = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.email} - {self.statut} - {self.transaction_id}"