from django.db import migrations


def seed_teacher_link_type(apps, schema_editor):
    CatalogItem = apps.get_model("core", "CatalogItem")

    CatalogItem.objects.update_or_create(
        catalog_type="teacher_link_type",
        name="Vinculacion",
        defaults={"description": "Tipo de vinculacion docente por defecto", "is_active": True},
    )


def unseed_teacher_link_type(apps, schema_editor):
    CatalogItem = apps.get_model("core", "CatalogItem")
    CatalogItem.objects.filter(catalog_type="teacher_link_type", name="Vinculacion").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0011_seed_default_roles"),
    ]

    operations = [
        migrations.RunPython(seed_teacher_link_type, unseed_teacher_link_type),
    ]
