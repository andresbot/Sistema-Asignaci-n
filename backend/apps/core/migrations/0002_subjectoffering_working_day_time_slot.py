from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectoffering",
            name="working_day",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subject_offerings",
                to="core.workingday",
            ),
        ),
        migrations.AddField(
            model_name="subjectoffering",
            name="time_slot",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="subject_offerings",
                to="core.timeslot",
            ),
        ),
    ]