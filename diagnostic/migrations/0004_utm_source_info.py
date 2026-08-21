from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("diagnostic", "0003_personnalisation_tracking"),
    ]

    operations = [
        migrations.AddField(
            model_name="diagnosticreponse",
            name="utm_source_info",
            field=models.CharField(
                blank=True,
                default="",
                max_length=100,
                verbose_name="Audience / origine détaillée",
            ),
        ),
        migrations.AddIndex(
            model_name="diagnosticreponse",
            index=models.Index(
                fields=["utm_source_info", "date_creation"],
                name="diag_srcinfo_date_idx",
            ),
        ),
    ]
