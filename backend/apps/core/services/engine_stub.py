from apps.core.models import Classroom, SubjectOffering, TimeSlot, WorkingDay
from apps.core.services.programming_service import update_subject_offering


def _find_first_slot_and_classroom(offering, academic_period):
    working_days = list(WorkingDay.objects.filter(is_active=True).order_by("day_of_week"))
    time_slots = list(TimeSlot.objects.filter(is_active=True).order_by("start_time"))
    classrooms = list(Classroom.objects.filter(is_active=True).order_by("code"))

    for wd in working_days:
        for ts in time_slots:
            for classroom in classrooms:
                if offering.student_count and classroom.capacity < offering.student_count:
                    continue
                if offering.required_space_type and getattr(classroom, "space_type", None) != offering.required_space_type:
                    continue
                if offering.requires_accessible_classroom and not getattr(classroom, "is_accessible", False):
                    continue

                occupied = SubjectOffering.objects.filter(
                    academic_period=academic_period,
                    working_day=wd,
                    time_slot=ts,
                    assigned_classroom=classroom,
                    is_active=True,
                ).exists()
                if occupied:
                    continue

                return wd, ts, classroom

    return None, None, None


def run_engine_stub(execution):
    academic_period = execution.academic_period
    assignments = []
    unassigned = []

    offerings = list(SubjectOffering.objects.filter(academic_period=academic_period, is_active=True))

    for off in offerings:
        if off.working_day is not None and off.time_slot is not None and off.assigned_classroom is not None:
            assignments.append(
                {
                    "subject_offering_id": off.id,
                    "codigo": off.subject.code,
                    "grupo": off.subject_group.identifier if off.subject_group else None,
                    "working_day": off.working_day.name if off.working_day else None,
                    "time_slot": off.time_slot.name if off.time_slot else None,
                    "classroom_code": off.assigned_classroom.code if off.assigned_classroom else None,
                }
            )
            continue

        wd, ts, classroom = _find_first_slot_and_classroom(off, academic_period)
        if wd and ts and classroom:
            try:
                update_subject_offering(
                    off,
                    subject=off.subject,
                    subject_group=off.subject_group,
                    working_day=wd,
                    time_slot=ts,
                    required_space_type=off.required_space_type,
                    teacher=off.teacher,
                    student_count=off.student_count,
                    requires_accessible_classroom=off.requires_accessible_classroom,
                    academic_program=off.academic_program,
                    academic_period=off.academic_period,
                    semester=off.semester,
                    is_active=off.is_active,
                )
                off.assigned_classroom = classroom
                off.schedule_failure_reason = ""
                off.save(update_fields=["assigned_classroom", "schedule_failure_reason", "updated_at"])
                assignments.append(
                    {
                        "subject_offering_id": off.id,
                        "codigo": off.subject.code,
                        "grupo": off.subject_group.identifier if off.subject_group else None,
                        "working_day": wd.name,
                        "time_slot": ts.name,
                        "classroom_code": classroom.code,
                    }
                )
            except Exception as exc:
                off.schedule_failure_reason = f"stub_error: {str(exc)}"
                off.save(update_fields=["schedule_failure_reason", "updated_at"])
                unassigned.append({"subject_offering_id": off.id, "reason": off.schedule_failure_reason})
        else:
            reason = "sin salones/franjas disponibles (stub)"
            off.schedule_failure_reason = reason
            off.save(update_fields=["schedule_failure_reason", "updated_at"])
            unassigned.append({"subject_offering_id": off.id, "reason": reason})

    return {"assignments": assignments, "unassigned": unassigned}
