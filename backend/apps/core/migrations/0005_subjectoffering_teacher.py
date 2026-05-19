import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0004_subjectoffering_required_space_type"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectoffering",
            name="teacher",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="subject_offerings",
                to="core.teacher",
            ),
        ),
    ]
