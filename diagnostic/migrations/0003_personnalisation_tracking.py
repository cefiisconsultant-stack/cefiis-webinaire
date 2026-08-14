import uuid

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("diagnostic", "0002_diagnostic_v2")]

    operations = [
        migrations.AddField(
            model_name="diagnosticevenement",
            name="event_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="consentement_diagnostic",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="consentement_marketing",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="device",
            field=models.CharField(blank=True, default="", max_length=20),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="landing_path",
            field=models.CharField(blank=True, default="", max_length=255),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="referrer",
            field=models.CharField(blank=True, default="", max_length=500),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="segment",
            field=models.CharField(
                blank=True,
                choices=[
                    ("exploration", "Exploration encadrée"),
                    ("fondations", "Fondations"),
                    ("structuration", "Structuration"),
                    ("test_marche", "Test du marché"),
                    ("pret_lancer", "Prêt à lancer"),
                    ("consultant_lancement", "Consultant — lancement actif"),
                    ("consultant_structuration", "Consultant — structuration commerciale"),
                    ("consultant_croissance", "Consultant — consolidation et croissance"),
                ],
                db_index=True,
                default="",
                max_length=40,
            ),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="utm_content",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="utm_term",
            field=models.CharField(blank=True, default="", max_length=100),
        ),
        migrations.AlterField(
            model_name="diagnosticevenement",
            name="nom",
            field=models.CharField(
                choices=[
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
                ],
                db_index=True,
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="anciennete_consultant",
            field=models.CharField(
                blank=True,
                choices=[("moins1", "Moins d’un an"), ("1a3", "1 à 3 ans"), ("plus3", "Plus de 3 ans")],
                default="",
                max_length=20,
            ),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="difficulte",
            field=models.CharField(
                blank=True,
                choices=[("reseau", "Avoir un réseau et des relations"), ("vendre", "Savoir se vendre sans être commercial"), ("prix", "Fixer un prix et le défendre"), ("temps", "Trouver le temps avec un emploi"), ("credibilite", "Être crédible face aux cabinets établis"), ("autre", "Autre")],
                default="",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="difficulte_consultant",
            field=models.CharField(
                blank=True,
                choices=[("missions", "Trouver des missions régulièrement"), ("tarifs", "Facturer à leur juste valeur"), ("offre", "Structurer mon offre"), ("gestion", "Gérer plusieurs clients en même temps"), ("gros_contrats", "Passer aux gros contrats"), ("autre", "Autre")],
                default="",
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="motivation",
            field=models.CharField(
                choices=[("remuneration", "Mieux gagner ma vie"), ("independance", "Ne plus dépendre d’un seul employeur"), ("liberte", "Être plus libre dans mon organisation"), ("valorisation", "Faire payer une expertise construite pendant des années"), ("apres_carriere", "Construire une activité qui dure après ma carrière"), ("impact", "Avoir plus d’impact dans mon secteur"), ("autre", "Autre")],
                max_length=30,
            ),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="score",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="sollicitation",
            field=models.CharField(
                choices=[("souvent", "Souvent"), ("parfois", "Quelques fois"), ("jamais", "Pas encore")],
                max_length=20,
            ),
        ),
        migrations.AddIndex(
            model_name="diagnosticevenement",
            index=models.Index(
                fields=["nom", "date_creation"], name="diag_event_funnel_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="diagnosticevenement",
            index=models.Index(
                fields=["session_id", "date_creation"], name="diag_event_session_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="diagnosticreponse",
            index=models.Index(
                fields=["utm_campaign", "date_creation"], name="diag_utm_date_idx"
            ),
        ),
        migrations.AddIndex(
            model_name="diagnosticreponse",
            index=models.Index(
                fields=["segment", "date_creation"], name="diag_segment_date_idx"
            ),
        ),
    ]
