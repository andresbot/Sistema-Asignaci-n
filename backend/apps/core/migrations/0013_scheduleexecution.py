from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0012_seed_teacher_link_type"),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[
                migrations.RunSQL(
                    sql="""
                    CREATE TABLE IF NOT EXISTS core_scheduleexecution (
                        id integer NOT NULL PRIMARY KEY AUTOINCREMENT,
                        created_at datetime NOT NULL,
                        updated_at datetime NOT NULL,
                        status varchar(20) NOT NULL,
                        progress smallint unsigned NOT NULL CHECK (progress >= 0),
                        parameters text NOT NULL,
                        result_snapshot text NOT NULL,
                        error_message text NOT NULL,
                        started_at datetime NULL,
                        finished_at datetime NULL,
                        academic_period_id bigint NOT NULL REFERENCES core_academicperiod (id) DEFERRABLE INITIALLY DEFERRED,
                        requested_by_id integer NOT NULL REFERENCES auth_user (id) DEFERRABLE INITIALLY DEFERRED
                    );
                    """,
                    reverse_sql="DROP TABLE IF EXISTS core_scheduleexecution;",
                )
            ],
            state_operations=[
                migrations.CreateModel(
                    name="ScheduleExecution",
                    fields=[
                        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                        ("created_at", models.DateTimeField(auto_now_add=True)),
                        ("updated_at", models.DateTimeField(auto_now=True)),
                        (
                            "status",
                            models.CharField(
                                choices=[
                                    ("pending", "Pendiente"),
                                    ("running", "En ejecucion"),
                                    ("completed", "Completado"),
                                    ("failed", "Fallido"),
                                ],
                                default="pending",
                                max_length=20,
                            ),
                        ),
                        ("progress", models.PositiveSmallIntegerField(default=0)),
                        ("parameters", models.JSONField(blank=True, default=dict)),
                        ("result_snapshot", models.JSONField(blank=True, default=dict)),
                        ("error_message", models.TextField(blank=True)),
                        ("started_at", models.DateTimeField(blank=True, null=True)),
                        ("finished_at", models.DateTimeField(blank=True, null=True)),
                        (
                            "academic_period",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.PROTECT,
                                related_name="schedule_executions",
                                to="core.academicperiod",
                            ),
                        ),
                        (
                            "requested_by",
                            models.ForeignKey(
                                on_delete=django.db.models.deletion.CASCADE,
                                related_name="schedule_executions",
                                to=settings.AUTH_USER_MODEL,
                            ),
                        ),
                    ],
                    options={
                        "ordering": ["-created_at", "-id"],
                    },
                ),
            ],
        ),
    ]
