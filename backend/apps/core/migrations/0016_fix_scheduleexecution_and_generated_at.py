"""
Migration 0016 — Repair migration gaps that exist in production.

Two schema elements were never applied to the remote database:

  1. core_academicperiod.schedule_generated_at  (declared in 0003 but the
     column was absent from Supabase/Render).

  2. core_scheduleexecution table  (migration 0013 used
     SeparateDatabaseAndState with empty database_operations, so the table
     was never created by any migration run).

Both operations are written with IF NOT EXISTS / IF NOT EXISTS so they are
safe to run against databases that already received a manual fix.
"""

from django.conf import settings
from django.db import migrations


CREATE_SCHEDULEEXECUTION = """
CREATE TABLE IF NOT EXISTS core_scheduleexecution (
    id              BIGSERIAL PRIMARY KEY,
    created_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    status          VARCHAR(20)  NOT NULL DEFAULT 'pending',
    progress        SMALLINT     NOT NULL DEFAULT 0,
    parameters      JSONB        NOT NULL DEFAULT '{}'::jsonb,
    result_snapshot JSONB        NOT NULL DEFAULT '{}'::jsonb,
    error_message   TEXT         NOT NULL DEFAULT '',
    started_at      TIMESTAMP WITH TIME ZONE NULL,
    finished_at     TIMESTAMP WITH TIME ZONE NULL,
    academic_period_id BIGINT NOT NULL
        REFERENCES core_academicperiod(id)
        ON DELETE RESTRICT
        DEFERRABLE INITIALLY DEFERRED,
    requested_by_id INTEGER NOT NULL
        REFERENCES auth_user(id)
        ON DELETE CASCADE
        DEFERRABLE INITIALLY DEFERRED
);
"""

CREATE_SCHEDULEEXECUTION_INDEXES = """
CREATE INDEX IF NOT EXISTS core_scheduleexecution_period_idx
    ON core_scheduleexecution(academic_period_id);
CREATE INDEX IF NOT EXISTS core_scheduleexecution_user_idx
    ON core_scheduleexecution(requested_by_id);
"""

ADD_SCHEDULE_GENERATED_AT = """
ALTER TABLE core_academicperiod
    ADD COLUMN IF NOT EXISTS schedule_generated_at
    TIMESTAMP WITH TIME ZONE NULL;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0015_academicperiod_unique_active_code"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            sql=ADD_SCHEDULE_GENERATED_AT,
            reverse_sql=migrations.RunSQL.noop,
        ),
        migrations.RunSQL(
            sql=CREATE_SCHEDULEEXECUTION + CREATE_SCHEDULEEXECUTION_INDEXES,
            reverse_sql="DROP TABLE IF EXISTS core_scheduleexecution;",
        ),
    ]
