from collections import defaultdict

from apps.core.models import Subject, SubjectOffering
from apps.core.services.programming_service import get_offering_non_assignable_reason


def _serialize_offering(offering):
    return {
        "id": offering.id,
        "subject": {
            "id": offering.subject.id,
            "code": offering.subject.code,
            "name": offering.subject.name,
        },
        "subject_group": {
            "id": offering.subject_group.id if offering.subject_group else None,
            "identifier": offering.subject_group.identifier if offering.subject_group else None,
        },
        "teacher": {
            "id": offering.teacher.id,
            "first_name": offering.teacher.first_name,
            "last_name": offering.teacher.last_name,
        }
        if offering.teacher
        else None,
        "working_day": {
            "id": offering.working_day.id if offering.working_day else None,
            "day_of_week": offering.working_day.day_of_week if offering.working_day else None,
            "name": offering.working_day.name if offering.working_day else None,
        },
        "time_slot": {
            "id": offering.time_slot.id if offering.time_slot else None,
            "start_time": offering.time_slot.start_time.isoformat() if offering.time_slot else None,
            "end_time": offering.time_slot.end_time.isoformat() if offering.time_slot else None,
            "name": offering.time_slot.name if offering.time_slot else None,
        },
        "required_space_type": {
            "id": offering.required_space_type.id if offering.required_space_type else None,
            "name": offering.required_space_type.name if offering.required_space_type else None,
        }
        if offering.required_space_type
        else None,
        "student_count": offering.student_count,
        "requires_accessible_classroom": offering.requires_accessible_classroom,
        "semester": offering.semester,
        "academic_program": {
            "id": offering.academic_program.id,
            "code": offering.academic_program.code,
            "name": offering.academic_program.name,
        },
    }


def _append_issue(issues, code, title, message, offerings, severity="error"):
    issues.append(
        {
            "code": code,
            "severity": severity,
            "title": title,
            "message": message,
            "offerings": [_serialize_offering(offering) for offering in offerings],
        }
    )


def validate_schedule_before_execution(academic_period):
    offerings = list(
        SubjectOffering.objects.select_related(
            "subject",
            "subject_group",
            "working_day",
            "time_slot",
            "teacher",
            "required_space_type",
            "academic_program",
        ).filter(academic_period=academic_period, is_active=True)
    )

    issues = []
    unique_issue_offerings = set()

    for offering in offerings:
        if offering.working_day is None or offering.time_slot is None:
            _append_issue(
                issues,
                code="missing_slot",
                title="Asignatura sin franja horaria",
                message=(
                    f"{offering.subject.code}"
                    f"{(' - ' + offering.subject_group.identifier) if offering.subject_group else ''}"
                    " no tiene dia o franja asignada."
                ),
                offerings=[offering],
            )
            unique_issue_offerings.add(offering.id)

        if offering.teacher is None:
            _append_issue(
                issues,
                code="missing_teacher",
                title="Asignatura sin docente",
                message=(
                    f"{offering.subject.code}"
                    f"{(' - ' + offering.subject_group.identifier) if offering.subject_group else ''}"
                    " no tiene docente asignado."
                ),
                offerings=[offering],
            )
            unique_issue_offerings.add(offering.id)

        if offering.student_count is None or offering.student_count <= 0:
            _append_issue(
                issues,
                code="missing_capacity",
                title="Asignatura sin cupo",
                message=(
                    f"{offering.subject.code}"
                    f"{(' - ' + offering.subject_group.identifier) if offering.subject_group else ''}"
                    " no tiene cupo registrado o es invalido."
                ),
                offerings=[offering],
            )
            unique_issue_offerings.add(offering.id)

        is_virtual = offering.subject.class_type == Subject.CLASS_TYPE_VIRTUAL
        if not is_virtual and offering.required_space_type is None:
            _append_issue(
                issues,
                code="missing_space_type",
                title="Asignatura sin tipo de espacio",
                message=(
                    f"{offering.subject.code}"
                    f"{(' - ' + offering.subject_group.identifier) if offering.subject_group else ''}"
                    " no tiene tipo de espacio requerido."
                ),
                offerings=[offering],
            )
            unique_issue_offerings.add(offering.id)

        non_assignable_reason = get_offering_non_assignable_reason(offering)
        if non_assignable_reason:
            _append_issue(
                issues,
                code="non_assignable_capacity",
                title="Sin disponibilidad de salones",
                message=(
                    f"{offering.subject.code}"
                    f"{(' - ' + offering.subject_group.identifier) if offering.subject_group else ''}"
                    f" no es asignable: {non_assignable_reason}."
                ),
                offerings=[offering],
            )
            unique_issue_offerings.add(offering.id)

    teacher_groups = defaultdict(list)
    for offering in offerings:
        if offering.teacher_id and offering.working_day_id and offering.time_slot_id:
            teacher_groups[(offering.teacher_id, offering.working_day_id, offering.time_slot_id)].append(offering)

    for conflict_offerings in teacher_groups.values():
        if len(conflict_offerings) < 2:
            continue

        teacher = conflict_offerings[0].teacher
        working_day = conflict_offerings[0].working_day
        time_slot = conflict_offerings[0].time_slot
        course_labels = [
            f"{offering.subject.code}{(' - ' + offering.subject_group.identifier) if offering.subject_group else ''}"
            for offering in conflict_offerings
        ]
        _append_issue(
            issues,
            code="teacher_conflict",
            title="Conflicto de docente en la misma franja",
            message=(
                f"El docente {teacher.first_name} {teacher.last_name} tiene "
                f"{len(conflict_offerings)} asignaturas en {working_day.name} "
                f"{time_slot.name}: {', '.join(course_labels)}."
            ),
            offerings=conflict_offerings,
        )
        unique_issue_offerings.update(offering.id for offering in conflict_offerings)

    return {
        "academic_period": {
            "id": academic_period.id,
            "code": academic_period.code,
            "name": academic_period.name,
        },
        "can_run_algorithm": len(issues) == 0,
        "status": "ok" if len(issues) == 0 else "blocked",
        "summary": {
            "total_offerings": len(offerings),
            "issues_count": len(issues),
            "offerings_with_issues": len(unique_issue_offerings),
            "teacher_conflicts": sum(1 for issue in issues if issue["code"] == "teacher_conflict"),
            "missing_slot": sum(1 for issue in issues if issue["code"] == "missing_slot"),
            "missing_teacher": sum(1 for issue in issues if issue["code"] == "missing_teacher"),
            "missing_capacity": sum(1 for issue in issues if issue["code"] == "missing_capacity"),
            "missing_space_type": sum(1 for issue in issues if issue["code"] == "missing_space_type"),
            "non_assignable_capacity": sum(1 for issue in issues if issue["code"] == "non_assignable_capacity"),
        },
        "message": (
            "La programación no presenta inconsistencias criticas."
            if len(issues) == 0
            else "La programación tiene inconsistencias que deben corregirse antes de ejecutar el algoritmo."
        ),
        "issues": issues,
    }
