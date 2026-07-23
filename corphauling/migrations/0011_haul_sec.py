from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("corphauling", "0010_instellingen"),
    ]

    operations = [
        migrations.AddField(
            model_name="haul",
            name="start_sec",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="haul",
            name="end_sec",
            field=models.FloatField(blank=True, null=True),
        ),
    ]
