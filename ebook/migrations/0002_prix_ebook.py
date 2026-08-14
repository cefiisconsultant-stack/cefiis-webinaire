from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [("ebook", "0001_initial")]

    operations = [
        migrations.AlterField(
            model_name="ebookachat",
            name="montant",
            field=models.PositiveIntegerField(default=2000),
        ),
    ]
