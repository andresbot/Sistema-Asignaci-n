from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_subjectoffering_horario_fields"),
    ]

    operations = [
        migrations.AddField(
            model_name="subjectoffering",
            name="requires_accessible_classroom",
            field=models.BooleanField(default=False),
        ),
    ]