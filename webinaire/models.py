# reservations/models.py
from django.db import models
from django.utils import timezone

class ReservationWebinaire(models.Model):
    NIVEAU_ETUDE_CHOICES = [
        ('BAC+5', 'BAC+5'),
        ('BAC+3', 'BAC+3'),
        ('BAC+7', 'BAC+8'),
        ('Etudiant', 'Étudiant'),
        ('Non spécifié', 'Non spécifié'),  # Ajoutez une valeur par défaut
    ]
    prenom = models.CharField(max_length=100)
    nom = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    profession = models.CharField(max_length=150, blank=True, null=True)
    date_inscription = models.DateTimeField(auto_now_add=True)
    niveau_etude = models.CharField(
        max_length=20, 
        choices=NIVEAU_ETUDE_CHOICES, 
        default='Non spécifié',  # Ajoutez une valeur par défaut
        # blank=True,  # Rend le champ optionnel dans les formulaires
        # null=True    # Permet les valeurs NULL en base de données
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
