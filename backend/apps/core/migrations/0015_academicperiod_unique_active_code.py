from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0014_catalogitem_unique_active_name"),
    ]

    operations = [
        migrations.AlterField(
            model_name="academicperiod",
            name="code",
            field=models.CharField(max_length=20),
        ),
        migrations.AddConstraint(
            model_name="academicperiod",
            constraint=models.UniqueConstraint(
                fields=["code"],
                condition=models.Q(("is_active", True)),
                name="unique_active_academic_period_code",
            ),
        ),
    ]
