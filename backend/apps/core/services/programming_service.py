from django.db import IntegrityError, transaction

from apps.core.models import AcademicPeriod, SubjectOffering

from .config_service import ConfigValidationError


def get_active_academic_period():
    return AcademicPeriod.objects.filter(is_active=True).order_by("-start_date", "-id").first()


@transaction.atomic
def create_subject_offering(
    *,
    subject,
    subject_group,
    working_day,
    time_slot,
    academic_program,
    academic_period=None,
    semester,
    is_active=True,
):
    if academic_period is None:
        academic_period = get_active_academic_period()
    if academic_period is None:
        raise ConfigValidationError("No existe un periodo academico activo.")

    if subject_group.subject_id != subject.id:
        raise ConfigValidationError("El grupo seleccionado no pertenece a la asignatura.")
    if working_day is None:
        raise ConfigValidationError("El dia laborable es obligatorio.", field="working_day_id")
    if time_slot is None:
        raise ConfigValidationError("La franja horaria es obligatoria.", field="time_slot_id")
    if not working_day.is_active:
        raise ConfigValidationError("El dia seleccionado no esta habilitado.", field="working_day_id")
    if not time_slot.is_active:
        raise ConfigValidationError("La franja seleccionada no esta habilitada.", field="time_slot_id")

    try:
        return SubjectOffering.objects.create(
            subject=subject,
            subject_group=subject_group,
            working_day=working_day,
            time_slot=time_slot,
            academic_program=academic_program,
            academic_period=academic_period,
            semester=semester,
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe una programación con ese grupo para el periodo activo.") from exc


@transaction.atomic
def update_subject_offering(
    subject_offering,
    *,
    subject,
    subject_group,
    working_day,
    time_slot,
    academic_program,
    academic_period,
    semester,
    is_active,
):
    if subject_group.subject_id != subject.id:
        raise ConfigValidationError("El grupo seleccionado no pertenece a la asignatura.")
    if working_day is None:
        raise ConfigValidationError("El dia laborable es obligatorio.", field="working_day_id")
    if time_slot is None:
        raise ConfigValidationError("La franja horaria es obligatoria.", field="time_slot_id")
    if not working_day.is_active:
        raise ConfigValidationError("El dia seleccionado no esta habilitado.", field="working_day_id")
    if not time_slot.is_active:
        raise ConfigValidationError("La franja seleccionada no esta habilitada.", field="time_slot_id")

    subject_offering.subject = subject
    subject_offering.subject_group = subject_group
    subject_offering.working_day = working_day
    subject_offering.time_slot = time_slot
    subject_offering.academic_program = academic_program
    subject_offering.academic_period = academic_period
    subject_offering.semester = semester
    subject_offering.is_active = is_active

    try:
        subject_offering.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe una programación con ese grupo para el periodo activo.") from exc

    return subject_offering