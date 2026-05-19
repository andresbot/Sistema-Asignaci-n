import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_academicperiod_schedule_generated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectoffering",
            name="required_space_type",
            field=models.ForeignKey(
                blank=True,
                limit_choices_to={"catalog_type": "academic_space_type"},
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subject_offerings",
                to="core.catalogitem",
            ),
        ),
    ]
