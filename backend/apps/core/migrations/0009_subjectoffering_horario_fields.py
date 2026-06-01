import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("core", "0008_academicperiod_is_schedule_published_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectoffering",
            name="assigned_classroom",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="subject_offerings",
                to="core.classroom",
            ),
        ),
        migrations.AddField(
            model_name="subjectoffering",
            name="schedule_failure_reason",
            field=models.TextField(blank=True, null=True),
        ),
    ]
