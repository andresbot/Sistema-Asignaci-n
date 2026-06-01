"""Add class_type_item FK to Subject and migrate existing values to CatalogItem

Revision ID: 0004_subject_class_type_item
Revises: 0003_academicperiod_schedule_generated_at
Create Date: 2026-05-11 00:00
"""
from django.db import migrations, models


def create_class_type_items_and_map(apps, schema_editor):
    CatalogItem = apps.get_model("core", "CatalogItem")
    Subject = apps.get_model("core", "Subject")

    # Ensure catalog items for presencial and virtual exist
    presencial, _ = CatalogItem.objects.get_or_create(
        catalog_type="class_type",
        name="Presencial",
        defaults={"description": "Presencial", "is_active": True},
    )
    virtual, _ = CatalogItem.objects.get_or_create(
        catalog_type="class_type",
        name="Virtual",
        defaults={"description": "Virtual", "is_active": True},
    )

    # Map existing Subject.class_type values
    for subj in Subject.objects.all():
        if subj.class_type == "presencial":
            subj.class_type_item_id = presencial.id
            subj.save(update_fields=["class_type_item_id"])
        elif subj.class_type == "virtual":
            subj.class_type_item_id = virtual.id
            subj.save(update_fields=["class_type_item_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0003_academicperiod_schedule_generated_at"),
    ]

    operations = [
        migrations.AddField(
            model_name="subject",
            name="class_type_item",
            field=models.ForeignKey(
                null=True,
                blank=True,
                on_delete=models.PROTECT,
                related_name="subjects",
                to="core.catalogitem",
            ),
        ),
        migrations.RunPython(create_class_type_items_and_map, migrations.RunPython.noop),
    ]
