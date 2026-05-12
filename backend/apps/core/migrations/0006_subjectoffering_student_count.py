from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0005_subjectoffering_teacher"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectoffering",
            name="student_count",
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
    ]
