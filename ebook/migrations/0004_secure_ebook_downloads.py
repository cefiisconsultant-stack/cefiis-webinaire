import datetime

from django.db import migrations, models
import django.db.models.deletion
from django.utils import timezone


def activer_anciens_achats_payes(apps, schema_editor):
    EbookAchat = apps.get_model("ebook", "EbookAchat")
    expiration = timezone.now() + datetime.timedelta(hours=72)
    EbookAchat.objects.filter(
        statut="paye",
        expiration_telechargement__isnull=True,
    ).update(expiration_telechargement=expiration)


class Migration(migrations.Migration):
    dependencies = [
        ("ebook", "0003_diagnostic_attribution"),
    ]

    operations = [
        migrations.AddField(
            model_name="ebookachat",
            name="dernier_telechargement_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="ebookachat",
            name="expiration_telechargement",
            field=models.DateTimeField(blank=True, db_index=True, null=True),
        ),
        migrations.AddField(
            model_name="ebookachat",
            name="nombre_telechargements",
            field=models.PositiveSmallIntegerField(default=0),
        ),
        migrations.CreateModel(
            name="EbookTelechargementEvenement",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "resultat",
                    models.CharField(
                        choices=[
                            ("autorise", "Autorisé"),
                            ("expire", "Lien expiré"),
                            ("limite", "Limite atteinte"),
                            ("fichier_absent", "Fichier absent"),
                        ],
                        max_length=20,
                    ),
                ),
                (
                    "compteur_apres",
                    models.PositiveSmallIntegerField(default=0),
                ),
                (
                    "empreinte_ip",
                    models.CharField(blank=True, default="", max_length=64),
                ),
                (
                    "user_agent",
                    models.CharField(blank=True, default="", max_length=255),
                ),
                (
                    "date_creation",
                    models.DateTimeField(auto_now_add=True, db_index=True),
                ),
                (
                    "achat",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="evenements_telechargement",
                        to="ebook.ebookachat",
                    ),
                ),
            ],
            options={
                "verbose_name": "événement de téléchargement",
                "verbose_name_plural": "événements de téléchargement",
                "ordering": ("-date_creation",),
            },
        ),
        migrations.RunPython(
            activer_anciens_achats_payes,
            migrations.RunPython.noop,
        ),
    ]

