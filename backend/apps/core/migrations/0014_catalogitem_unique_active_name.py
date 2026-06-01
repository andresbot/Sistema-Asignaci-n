from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_scheduleexecution"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="catalogitem",
            name="unique_catalog_item_per_type",
        ),
        migrations.AddConstraint(
            model_name="catalogitem",
            constraint=models.UniqueConstraint(
                fields=["catalog_type", "name"],
                condition=models.Q(("is_active", True)),
                name="unique_catalog_item_per_type",
            ),
        ),
    ]
