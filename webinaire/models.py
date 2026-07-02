# reservations/models.py
from django.db import models
from django.utils import timezone

# reservations/models.py
from django.db import models

class ReservationWebinaire(models.Model):
    NIVEAU_ETUDE_CHOICES = [
        ('BAC+5', 'BAC+5'),
        ('BAC+3', 'BAC+3'),
        ('BAC+7', 'BAC+8'),      # Attention ici, le code original avait 'BAC+8' au lieu de 'BAC+7'
        ('Etudiant', 'Étudiant'),
        ('Non spécifié', 'Non spécifié'),
    ]
    prenom = models.CharField(max_length=100)
    nom = models.CharField(
        max_length=100,
        blank=True,         # Permet de ne pas renseigner le champ dans les formulaires
        null=True,          # Autorise NULL en base de données
        default=''          # Facultatif, pour éviter les migrations avec valeur par défaut
    )
    email = models.EmailField(unique=True)
    profession = models.CharField(max_length=150, blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    niveau_etude = models.CharField(
        max_length=20,
        choices=NIVEAU_ETUDE_CHOICES,
        default='Non spécifié',
        blank=True,         # Facultatif dans les formulaires
        # null=True pas nécessaire car blank=True + default suffisent pour les champs texte
    )
    dans_sequence_opera = models.BooleanField(default=False)
    niveau_sequence = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.prenom} {self.nom} - {self.email}"


# class EmailTracking(models.Model):
#     email = models.EmailField()
#     email_name = models.CharField(max_length=100)  # ex: "soap_opera_3"
#     opened = models.BooleanField(default=False)
#     open_count = models.PositiveIntegerField(default=0)
#     last_opened_at = models.DateTimeField(null=True, blank=True)
#     # clicked_count = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return f"{self.email} - {self.email_name}"
