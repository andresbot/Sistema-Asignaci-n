import time
from threading import Thread

from django.db import close_old_connections
from django.utils import timezone

from apps.core.models import ScheduleExecution, SubjectOffering
from apps.core.serializers import HorarioOfferingSerializer, HorarioUnassignedSerializer
from apps.core.services.engine_stub import run_engine_stub


def _build_execution_snapshot(academic_period):
    assignments_queryset = (
        SubjectOffering.objects.select_related(
            "working_day",
            "time_slot",
            "subject",
            "teacher",
            "subject_group",
            "assigned_classroom",
            "assigned_classroom__campus",
        )
        .filter(academic_period=academic_period, is_active=True, working_day__isnull=False, time_slot__isnull=False)
        .order_by("working_day__day_of_week", "time_slot__start_time")
    )
    unassigned_queryset = (
        SubjectOffering.objects.select_related("subject", "subject_group", "academic_period")
        .filter(academic_period=academic_period, is_active=True, working_day__isnull=True)
        .order_by("subject__name")
    )

    assignments = HorarioOfferingSerializer(assignments_queryset, many=True).data
    unassigned = HorarioUnassignedSerializer(unassigned_queryset, many=True).data

    return {
        "assignments": assignments,
        "unassigned": unassigned,
        "summary": {
            "total_assignments": len(assignments),
            "total_unassigned": len(unassigned),
        },
    }


def run_schedule_execution(execution):
    total_generations = execution.parameters.get("generaciones", 10)
    try:
        total_generations = int(total_generations)
    except (TypeError, ValueError):
        total_generations = 10
    total_generations = max(1, total_generations)

    execution.status = ScheduleExecution.Status.RUNNING
    execution.progress = 5
    execution.started_at = timezone.now()
    execution.save(update_fields=["status", "progress", "started_at", "updated_at"])

    academic_period = execution.academic_period

    for generation in range(1, total_generations + 1):
        execution.progress = min(85, 5 + int((generation / total_generations) * 75))
        execution.result_snapshot = {
            "current_generation": generation,
            "total_generations": total_generations,
        }
        execution.save(update_fields=["progress", "result_snapshot", "updated_at"])
        time.sleep(0.02)

    try:
        engine_result = run_engine_stub(execution)
    except Exception as exc:
        execution.status = ScheduleExecution.Status.FAILED
        execution.progress = 100
        execution.error_message = f"Error ejecutando motor de programacion: {str(exc)}"
        execution.finished_at = timezone.now()
        execution.save(update_fields=["status", "progress", "error_message", "finished_at", "updated_at"])
        return execution

    snapshot = _build_execution_snapshot(academic_period)
    snapshot["current_generation"] = total_generations
    snapshot["total_generations"] = total_generations
    if engine_result:
        snapshot["engine_assignments_count"] = len(engine_result.get("assignments", []))
        snapshot["engine_unassigned_count"] = len(engine_result.get("unassigned", []))

    execution.result_snapshot = snapshot
    execution.status = ScheduleExecution.Status.COMPLETED
    execution.progress = 100
    execution.finished_at = timezone.now()
    execution.error_message = ""
    execution.save(
        update_fields=[
            "status",
            "progress",
            "result_snapshot",
            "error_message",
            "finished_at",
            "updated_at",
        ]
    )

    academic_period.schedule_generated_at = execution.finished_at
    academic_period.save(update_fields=["schedule_generated_at", "updated_at"])

    return execution


def _run_schedule_execution_worker(execution_id):
    close_old_connections()
    try:
        execution = ScheduleExecution.objects.select_related("academic_period").get(id=execution_id)
        run_schedule_execution(execution)
    except Exception:
        execution = ScheduleExecution.objects.filter(id=execution_id).select_related("academic_period").first()
        if execution is None:
            return

        execution.status = ScheduleExecution.Status.FAILED
        execution.progress = 100
        execution.error_message = "No se pudo ejecutar el motor de programacion."
        execution.finished_at = timezone.now()
        execution.save(
            update_fields=["status", "progress", "error_message", "finished_at", "updated_at"]
        )
    finally:
        close_old_connections()


def queue_schedule_execution(execution_id):
    worker = Thread(target=_run_schedule_execution_worker, args=(execution_id,), daemon=True)
    worker.start()
    return worker
