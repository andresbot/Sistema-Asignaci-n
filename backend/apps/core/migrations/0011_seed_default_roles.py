from django.db import migrations


def seed_default_roles(apps, schema_editor):
    Role = apps.get_model("core", "Role")

    default_roles = [
        ("Administrador", "Usuario con acceso completo al sistema"),
        ("Coordinador", "Usuario encargado de programacion y consulta administrativa"),
        ("Docente", "Usuario que consulta su horario publicado"),
        ("Estudiante", "Usuario que consulta su horario publicado"),
    ]

    for role_name, description in default_roles:
        Role.objects.update_or_create(
            name=role_name,
            defaults={"description": description, "is_active": True},
        )


def unseed_default_roles(apps, schema_editor):
    Role = apps.get_model("core", "Role")
    Role.objects.filter(name__in=["Administrador", "Coordinador", "Docente", "Estudiante"]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0010_subjectoffering_requires_accessible_classroom"),
    ]

    operations = [
        migrations.RunPython(seed_default_roles, unseed_default_roles),
    ]