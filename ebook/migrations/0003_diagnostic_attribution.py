from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("diagnostic", "0003_personnalisation_tracking"),
        ("ebook", "0002_prix_ebook"),
    ]

    operations = [
        migrations.AddField(
            model_name="ebookachat",
            name="diagnostic",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="achats_ebook",
                to="diagnostic.diagnosticreponse",
            ),
        ),
        migrations.AddField(
            model_name="ebookachat",
            name="diagnostic_session_id",
            field=models.UUIDField(blank=True, db_index=True, null=True),
        ),
    ]
