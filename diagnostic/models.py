import uuid

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from .countries import PAYS_CHOICES


class DiagnosticReponse(models.Model):
    SEGMENTS = [
        ("exploration", "Exploration encadrée"),
        ("fondations", "Fondations"),
        ("structuration", "Structuration"),
        ("test_marche", "Test du marché"),
        ("pret_lancer", "Prêt à lancer"),
        ("consultant_lancement", "Consultant — lancement actif"),
        ("consultant_structuration", "Consultant — structuration commerciale"),
        ("consultant_croissance", "Consultant — consolidation et croissance"),
    ]
    DOMAINES = [
        ("rh", "Ressources humaines"),
        ("projet", "Gestion de projet"),
        ("finance", "Finance & comptabilité"),
        ("education", "Éducation & formation"),
        ("sante", "Santé"),
        ("agri", "Agriculture & agro-industrie"),
        ("logistique", "Logistique & transport"),
        ("communication", "Communication & marketing"),
        ("numerique", "Informatique & numérique"),
        ("droit", "Droit & administration"),
        ("developpement", "Développement & ONG"),
        ("autre", "Autre"),
    ]
    EXPERIENCE = [
        ("moins5", "Moins de 5 ans"),
        ("5a10", "5 à 10 ans"),
        ("10a20", "10 à 20 ans"),
        ("plus20", "Plus de 20 ans"),
    ]
    SITUATIONS = [
        ("poste", "En poste, salarié(e)"),
        ("entrepreneur", "Entrepreneur(e)"),
        ("fin_contrat", "En fin de contrat ou de projet"),
        ("retraite", "Proche de la retraite"),
        ("etudiant", "Étudiant(e) ou jeune diplômé(e)"),
        ("sans_emploi", "Sans emploi actuellement"),
        ("consultant", "Déjà consultant(e) indépendant(e)"),
        ("autre", "Autre"),
    ]
    SOLLICITATIONS = [
        ("souvent", "Souvent"),
        ("parfois", "Quelques fois"),
        ("jamais", "Pas encore"),
    ]
    MOTIVATIONS = [
        ("remuneration", "Mieux gagner ma vie"),
        ("independance", "Ne plus dépendre d’un seul employeur"),
        ("liberte", "Être plus libre dans mon organisation"),
        ("valorisation", "Faire payer une expertise construite pendant des années"),
        ("apres_carriere", "Construire une activité qui dure après ma carrière"),
        ("impact", "Avoir plus d’impact dans mon secteur"),
        ("autre", "Autre"),
    ]
    DIFFICULTES = [
        ("reseau", "Avoir un réseau et des relations"),
        ("vendre", "Savoir se vendre sans être commercial"),
        ("prix", "Fixer un prix et le défendre"),
        ("temps", "Trouver le temps avec un emploi"),
        ("credibilite", "Être crédible face aux cabinets établis"),
        ("autre", "Autre"),
    ]
    ANCIENNETE_CONSULTANT = [
        ("moins1", "Moins d’un an"),
        ("1a3", "1 à 3 ans"),
        ("plus3", "Plus de 3 ans"),
    ]
    DIFFICULTES_CONSULTANT = [
        ("missions", "Trouver des missions régulièrement"),
        ("tarifs", "Facturer à leur juste valeur"),
        ("offre", "Structurer mon offre"),
        ("gestion", "Gérer plusieurs clients en même temps"),
        ("gros_contrats", "Passer aux gros contrats"),
        ("autre", "Autre"),
    ]

    public_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    session_id = models.UUIDField(default=uuid.uuid4, db_index=True, editable=False)

    prenom = models.CharField(max_length=100)
    pays = models.CharField(max_length=2, choices=PAYS_CHOICES, default="BJ")
    indicatif = models.CharField(max_length=6, default="+229")
    numero_national = models.CharField(max_length=24, default="")
    whatsapp = models.CharField(max_length=30)
    email = models.EmailField(blank=True, default="")

    domaine = models.CharField(max_length=30, choices=DOMAINES)
    domaine_autre = models.CharField(max_length=150, blank=True, default="")
    experience = models.CharField(max_length=20, choices=EXPERIENCE)
    situation = models.CharField(max_length=20, choices=SITUATIONS)
    situation_autre = models.CharField(max_length=150, blank=True, default="")
    sollicitation = models.CharField(max_length=20, choices=SOLLICITATIONS)
    motivation = models.CharField(max_length=30, choices=MOTIVATIONS)
    motivation_autre = models.CharField(max_length=200, blank=True, default="")

    a_positionnement = models.BooleanField(default=False)
    a_offre = models.BooleanField(default=False)
    a_tarifs = models.BooleanField(default=False)
    a_prospection = models.BooleanField(default=False)

    difficulte = models.CharField(max_length=30, choices=DIFFICULTES, blank=True, default="")
    difficulte_autre = models.CharField(max_length=250, blank=True, default="")
    anciennete_consultant = models.CharField(
        max_length=20, choices=ANCIENNETE_CONSULTANT, blank=True, default=""
    )
    difficulte_consultant = models.CharField(
        max_length=30, choices=DIFFICULTES_CONSULTANT, blank=True, default=""
    )
    difficulte_consultant_autre = models.CharField(max_length=250, blank=True, default="")

    score = models.PositiveSmallIntegerField(default=0)
    duree_secondes = models.PositiveIntegerField(null=True, blank=True)
    utm_source = models.CharField(max_length=50, blank=True, default="")
    utm_medium = models.CharField(max_length=50, blank=True, default="")
    utm_campaign = models.CharField(max_length=100, blank=True, default="")
    utm_source_info = models.CharField(
        max_length=100,
        blank=True,
        default="",
        verbose_name="Audience / origine détaillée",
    )
    gclid = models.CharField(max_length=255, blank=True, default="")
    utm_content = models.CharField(max_length=100, blank=True, default="")
    utm_term = models.CharField(max_length=100, blank=True, default="")
    device = models.CharField(max_length=20, blank=True, default="")
    landing_path = models.CharField(max_length=255, blank=True, default="")
    referrer = models.CharField(max_length=500, blank=True, default="")
    segment = models.CharField(
        max_length=40, choices=SEGMENTS, blank=True, default="", db_index=True
    )
    consentement_diagnostic = models.BooleanField(default=False)
    consentement_marketing = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)

    note_formulaire = models.PositiveSmallIntegerField(
        null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    commentaire_formulaire = models.TextField(blank=True, default="")
    date_feedback = models.DateTimeField(null=True, blank=True)

    contacte = models.BooleanField(default=False, verbose_name="Contacté en privé")
    ebook_achete = models.BooleanField(default=False)
    notes = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Réponse au diagnostic"
        verbose_name_plural = "Réponses au diagnostic"
        indexes = [
            models.Index(fields=["utm_campaign", "date_creation"], name="diag_utm_date_idx"),
            models.Index(
                fields=["utm_source_info", "date_creation"],
                name="diag_srcinfo_date_idx",
            ),
            models.Index(fields=["segment", "date_creation"], name="diag_segment_date_idx"),
        ]

    def __str__(self):
        return f"{self.prenom} — {self.get_domaine_display()} ({self.date_creation:%d/%m/%Y})"

    @property
    def est_consultant(self):
        return self.situation == "consultant"

    @property
    def elements_manquants(self):
        axes = [
            (self.a_positionnement, "un positionnement précis"),
            (self.a_offre, "une offre structurée"),
            (self.a_tarifs, "une grille tarifaire"),
            (self.a_prospection, "une méthode de prospection"),
        ]
        return [label for complete, label in axes if not complete]

    def calculer_score(self):
        self.score = sum(
            [self.a_positionnement, self.a_offre, self.a_tarifs, self.a_prospection]
        )
        return self.score


class DiagnosticEvenement(models.Model):
    EVENEMENTS = [
        ("view", "Vue du diagnostic"),
        ("start", "Démarrage"),
        ("step_view", "Étape affichée"),
        ("step_complete", "Étape terminée"),
        ("validation_error", "Erreur de validation"),
        ("abandon", "Abandon"),
        ("complete", "Diagnostic terminé"),
        ("result_view", "Résultat affiché"),
        ("ebook_click", "Clic ebook"),
        ("checkout_view", "Page de paiement affichée"),
        ("payment_started", "Paiement démarré"),
        ("purchase", "Achat ebook confirmé"),
        ("whatsapp_click", "Clic groupe WhatsApp"),
    ]

    event_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    session_id = models.UUIDField(db_index=True)
    reponse = models.ForeignKey(
        DiagnosticReponse,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="evenements",
    )
    nom = models.CharField(max_length=32, choices=EVENEMENTS, db_index=True)
    etape = models.PositiveSmallIntegerField(null=True, blank=True)
    ecran = models.CharField(max_length=32, blank=True, default="")
    duree_ms = models.PositiveIntegerField(null=True, blank=True)
    meta = models.JSONField(default=dict, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ["-date_creation"]
        verbose_name = "Événement de diagnostic"
        verbose_name_plural = "Événements de diagnostic"
        indexes = [
            models.Index(fields=["nom", "date_creation"], name="diag_event_funnel_idx"),
            models.Index(fields=["session_id", "date_creation"], name="diag_event_session_idx"),
        ]
