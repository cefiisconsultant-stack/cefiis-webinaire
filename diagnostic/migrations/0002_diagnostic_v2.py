import uuid

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


PAYS_CHOICES = [
    ("DZ", "🇩🇿 Algérie"), ("BJ", "🇧🇯 Bénin"), ("BF", "🇧🇫 Burkina Faso"),
    ("BI", "🇧🇮 Burundi"), ("CM", "🇨🇲 Cameroun"), ("CF", "🇨🇫 Centrafrique"),
    ("KM", "🇰🇲 Comores"), ("CG", "🇨🇬 Congo"), ("CD", "🇨🇩 Congo (RDC)"),
    ("CI", "🇨🇮 Côte d’Ivoire"), ("DJ", "🇩🇯 Djibouti"), ("GA", "🇬🇦 Gabon"),
    ("GN", "🇬🇳 Guinée"), ("GQ", "🇬🇶 Guinée équatoriale"),
    ("MG", "🇲🇬 Madagascar"), ("ML", "🇲🇱 Mali"), ("MA", "🇲🇦 Maroc"),
    ("MU", "🇲🇺 Maurice"), ("MR", "🇲🇷 Mauritanie"), ("NE", "🇳🇪 Niger"),
    ("RW", "🇷🇼 Rwanda"), ("SN", "🇸🇳 Sénégal"), ("SC", "🇸🇨 Seychelles"),
    ("TD", "🇹🇩 Tchad"), ("TG", "🇹🇬 Togo"), ("TN", "🇹🇳 Tunisie"),
]


def populate_uuids(apps, schema_editor):
    Reponse = apps.get_model("diagnostic", "DiagnosticReponse")
    for reponse in Reponse.objects.filter(public_id__isnull=True).iterator():
        reponse.public_id = uuid.uuid4()
        reponse.session_id = uuid.uuid4()
        reponse.save(update_fields=["public_id", "session_id"])


class Migration(migrations.Migration):
    dependencies = [("diagnostic", "0001_initial")]

    operations = [
        migrations.AddField(
            model_name="diagnosticreponse",
            name="public_id",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="session_id",
            field=models.UUIDField(null=True, editable=False),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="pays",
            field=models.CharField(choices=PAYS_CHOICES, default="BJ", max_length=2),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="indicatif",
            field=models.CharField(default="+229", max_length=6),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="numero_national",
            field=models.CharField(default="", max_length=24),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="situation_autre",
            field=models.CharField(blank=True, default="", max_length=150),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="duree_secondes",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="note_formulaire",
            field=models.PositiveSmallIntegerField(
                blank=True,
                null=True,
                validators=[
                    django.core.validators.MinValueValidator(1),
                    django.core.validators.MaxValueValidator(5),
                ],
            ),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="commentaire_formulaire",
            field=models.TextField(blank=True, default=""),
        ),
        migrations.AddField(
            model_name="diagnosticreponse",
            name="date_feedback",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="situation",
            field=models.CharField(
                choices=[
                    ("poste", "En poste, salarié(e)"),
                    ("entrepreneur", "Entrepreneur(e)"),
                    ("fin_contrat", "En fin de contrat ou de projet"),
                    ("retraite", "Proche de la retraite"),
                    ("etudiant", "Étudiant(e) ou jeune diplômé(e)"),
                    ("sans_emploi", "Sans emploi actuellement"),
                    ("consultant", "Déjà consultant(e) indépendant(e)"),
                    ("autre", "Autre"),
                ],
                max_length=20,
            ),
        ),
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="public_id",
            field=models.UUIDField(default=uuid.uuid4, editable=False, unique=True),
        ),
        migrations.AlterField(
            model_name="diagnosticreponse",
            name="session_id",
            field=models.UUIDField(db_index=True, default=uuid.uuid4, editable=False),
        ),
        migrations.CreateModel(
            name="DiagnosticEvenement",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("session_id", models.UUIDField(db_index=True)),
                ("nom", models.CharField(choices=[("view", "Vue du diagnostic"), ("start", "Démarrage"), ("step_view", "Étape affichée"), ("step_complete", "Étape terminée"), ("validation_error", "Erreur de validation"), ("abandon", "Abandon"), ("complete", "Diagnostic terminé"), ("result_view", "Résultat affiché"), ("ebook_click", "Clic ebook"), ("whatsapp_click", "Clic groupe WhatsApp")], db_index=True, max_length=32)),
                ("etape", models.PositiveSmallIntegerField(blank=True, null=True)),
                ("ecran", models.CharField(blank=True, default="", max_length=32)),
                ("duree_ms", models.PositiveIntegerField(blank=True, null=True)),
                ("meta", models.JSONField(blank=True, default=dict)),
                ("date_creation", models.DateTimeField(auto_now_add=True, db_index=True)),
                ("reponse", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="evenements", to="diagnostic.diagnosticreponse")),
            ],
            options={"verbose_name": "Événement de diagnostic", "verbose_name_plural": "Événements de diagnostic", "ordering": ["-date_creation"]},
        ),
    ]
