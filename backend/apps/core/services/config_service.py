from django.db import IntegrityError, transaction
from django.utils import timezone

from apps.core.models import (
    AcademicPeriod,
    AcademicProgram,
    CatalogItem,
    SpaceType,
    Subject,
    SubjectGroup,
    TimeSlot,
    WorkingDay,
)


class ConfigServiceError(Exception):
    pass


class ConfigValidationError(ConfigServiceError):
    def __init__(self, message, field=None):
        super().__init__(message)
        self.field = field


def _normalize_name(name):
    return (name or "").strip()


def _normalize_required_text(value, *, field, empty_message):
    normalized = (value or "").strip()
    if not normalized:
        raise ConfigValidationError(empty_message, field=field)
    return normalized


def _normalize_required_code(code):
    normalized_code = (code or "").strip()
    if not normalized_code:
        raise ConfigValidationError("El codigo del periodo es obligatorio.", field="code")
    return normalized_code


def _validate_period(start_date, end_date):
    if start_date > end_date:
        raise ConfigValidationError(
            "La fecha de fin debe ser mayor o igual a la fecha de inicio.",
            field="end_date",
        )


def _validate_day_of_week(day_of_week):
    if day_of_week < 1 or day_of_week > 7:
        raise ConfigValidationError("El dia laborable debe estar entre 1 y 7.", field="day_of_week")


def _validate_time_range(start_time, end_time):
    if start_time >= end_time:
        raise ConfigValidationError("La hora de fin debe ser mayor a la hora de inicio.", field="end_time")


def _validate_catalog_type(catalog_type):
    valid_types = {choice for choice, _label in CatalogItem.CatalogType.choices}
    if catalog_type not in valid_types:
        raise ConfigValidationError("El tipo de catalogo no es valido.", field="catalog_type")


def _catalog_type_label(catalog_type):
    return {
        CatalogItem.CatalogType.TEACHER_LINK_TYPE: "tipo de vinculacion docente",
        CatalogItem.CatalogType.CLASS_TYPE: "tipo de clase",
        CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE: "tipo de espacio academico",
    }.get(catalog_type, "tipo de catalogo")


def _ensure_period_code_unique(code, *, exclude_id=None):
    queryset = AcademicPeriod.objects.filter(code__iexact=code, is_active=True)
    if exclude_id is not None:
        queryset = queryset.exclude(id=exclude_id)
    if queryset.exists():
        raise ConfigValidationError("Ya existe un periodo con ese codigo.", field="code")


def _ensure_space_type_name_unique(name, *, exclude_id=None):
    queryset = SpaceType.objects.filter(name__iexact=name)
    if exclude_id is not None:
        queryset = queryset.exclude(id=exclude_id)
    if queryset.exists():
        raise ConfigValidationError("Ya existe un tipo de espacio con ese nombre.", field="name")


def _ensure_catalog_item_name_unique(catalog_type, name, *, exclude_id=None):
    queryset = CatalogItem.objects.filter(
        catalog_type=catalog_type,
        name__iexact=name,
        is_active=True,
    )
    if exclude_id is not None:
        queryset = queryset.exclude(id=exclude_id)
    if queryset.exists():
        raise ConfigValidationError(
            "Ya existe un valor para este tipo de catalogo con ese nombre.", field="name"
        )


def _validate_code(code):
    normalized_code = (code or "").strip()
    if not normalized_code:
        raise ConfigValidationError("El codigo es obligatorio.")
    return normalized_code


def _validate_required_name(name):
    normalized_name = _normalize_name(name)
    if not normalized_name:
        raise ConfigValidationError("El nombre es obligatorio.")
    return normalized_name


def _validate_identifier(identifier):
    normalized_identifier = _normalize_name(identifier)
    if not normalized_identifier:
        raise ConfigValidationError("El identificador es obligatorio.")
    return normalized_identifier


def _validate_positive_integer(value, field_label):
    if value is None or value <= 0:
        raise ConfigValidationError(f"{field_label} debe ser mayor a cero.")


SUBJECT_CREDITS_MAX = 20
SUBJECT_WEEKLY_HOURS_MAX = 40


def _validate_credits_range(credits):
    _validate_positive_integer(credits, "Los creditos")
    if credits > SUBJECT_CREDITS_MAX:
        raise ConfigValidationError(
            f"Los creditos no pueden superar {SUBJECT_CREDITS_MAX}.",
            field="credits",
        )


def _validate_weekly_hours_range(weekly_hours):
    _validate_positive_integer(weekly_hours, "La intensidad horaria")
    if weekly_hours > SUBJECT_WEEKLY_HOURS_MAX:
        raise ConfigValidationError(
            f"La intensidad horaria no puede superar {SUBJECT_WEEKLY_HOURS_MAX} horas semanales.",
            field="weekly_hours",
        )


def _validate_class_type(class_type):
    valid_types = {choice[0] for choice in Subject.CLASS_TYPE_CHOICES}
    legacy_map = {
        "teorica": Subject.CLASS_TYPE_PRESENCIAL,
        "practica": Subject.CLASS_TYPE_VIRTUAL,
    }

    normalized_class_type = legacy_map.get(class_type, class_type)
    if normalized_class_type not in valid_types:
        raise ConfigValidationError("El tipo de clase no es valido.")

    return normalized_class_type


def _calculate_difficulty(*, weekly_hours, capacity):
    _validate_positive_integer(weekly_hours, "La intensidad horaria")
    _validate_positive_integer(capacity, "El cupo")
    return weekly_hours * capacity


@transaction.atomic
def create_academic_period(
    *,
    code,
    name,
    start_date,
    end_date,
    is_active=True,
    is_schedule_published=False,
):
    normalized_code = _normalize_required_code(code)
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del periodo es obligatorio.",
    )
    _validate_period(start_date, end_date)
    _ensure_period_code_unique(normalized_code)

    try:
        published_at = timezone.now() if is_schedule_published else None
        return AcademicPeriod.objects.create(
            code=normalized_code,
            name=normalized_name,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
            is_schedule_published=is_schedule_published,
            schedule_published_at=published_at,
        )
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un periodo con ese codigo.", field="code") from exc


@transaction.atomic
def update_academic_period(period, *, code, name, start_date, end_date, is_active, is_schedule_published):
    normalized_code = _normalize_required_code(code)
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del periodo es obligatorio.",
    )
    _validate_period(start_date, end_date)
    _ensure_period_code_unique(normalized_code, exclude_id=period.id)

    period.code = normalized_code
    period.name = normalized_name
    period.start_date = start_date
    period.end_date = end_date
    period.is_active = is_active
    period.is_schedule_published = is_schedule_published
    if is_schedule_published and period.schedule_published_at is None:
        period.schedule_published_at = timezone.now()
    elif not is_schedule_published:
        period.schedule_published_at = None

    try:
        period.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un periodo con ese codigo.", field="code") from exc

    return period


@transaction.atomic
def publish_academic_period(period):
    period.is_schedule_published = True
    if period.schedule_published_at is None:
        period.schedule_published_at = timezone.now()
    period.save(update_fields=["is_schedule_published", "schedule_published_at", "updated_at"])
    return period


@transaction.atomic
def unpublish_academic_period(period):
    period.is_schedule_published = False
    period.schedule_published_at = None
    period.save(update_fields=["is_schedule_published", "schedule_published_at", "updated_at"])
    return period


@transaction.atomic
def create_working_day(*, day_of_week, name, is_active=True):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del dia laborable es obligatorio.",
    )
    _validate_day_of_week(day_of_week)

    try:
        return WorkingDay.objects.create(
            day_of_week=day_of_week,
            name=normalized_name,
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe ese dia laborable.", field="day_of_week") from exc


@transaction.atomic
def update_working_day(working_day, *, day_of_week, name, is_active):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del dia laborable es obligatorio.",
    )
    _validate_day_of_week(day_of_week)

    working_day.day_of_week = day_of_week
    working_day.name = normalized_name
    working_day.is_active = is_active

    try:
        working_day.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe ese dia laborable.", field="day_of_week") from exc

    return working_day


@transaction.atomic
def create_time_slot(*, name, start_time, end_time, is_active=True):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre de la franja es obligatorio.",
    )
    _validate_time_range(start_time, end_time)

    try:
        return TimeSlot.objects.create(
            name=normalized_name,
            start_time=start_time,
            end_time=end_time,
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError(
            "Ya existe una franja con ese nombre y horario.", field="name"
        ) from exc


@transaction.atomic
def update_time_slot(time_slot, *, name, start_time, end_time, is_active):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre de la franja es obligatorio.",
    )
    _validate_time_range(start_time, end_time)

    time_slot.name = normalized_name
    time_slot.start_time = start_time
    time_slot.end_time = end_time
    time_slot.is_active = is_active

    try:
        time_slot.save()
    except IntegrityError as exc:
        raise ConfigValidationError(
            "Ya existe una franja con ese nombre y horario.", field="name"
        ) from exc

    return time_slot


@transaction.atomic
def create_space_type(*, name, description="", is_active=True):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del tipo de espacio es obligatorio.",
    )
    _ensure_space_type_name_unique(normalized_name)

    try:
        return SpaceType.objects.create(
            name=normalized_name,
            description=(description or "").strip(),
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un tipo de espacio con ese nombre.", field="name") from exc


@transaction.atomic
def update_space_type(space_type, *, name, description, is_active):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del tipo de espacio es obligatorio.",
    )
    _ensure_space_type_name_unique(normalized_name, exclude_id=space_type.id)

    space_type.name = normalized_name
    space_type.description = (description or "").strip()
    space_type.is_active = is_active

    try:
        space_type.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un tipo de espacio con ese nombre.", field="name") from exc

    return space_type


@transaction.atomic
def create_catalog_item(*, catalog_type, name, description="", is_active=True):
    _validate_catalog_type(catalog_type)
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del catalogo es obligatorio.",
    )
    if is_active:
        _ensure_catalog_item_name_unique(catalog_type, normalized_name)

    try:
        return CatalogItem.objects.create(
            catalog_type=catalog_type,
            name=normalized_name,
            description=(description or "").strip(),
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError(
            f"Ya existe un {_catalog_type_label(catalog_type)} con ese nombre.",
            field="name",
        ) from exc


@transaction.atomic
def update_catalog_item(catalog_item, *, name, description, is_active):
    normalized_name = _normalize_required_text(
        name,
        field="name",
        empty_message="El nombre del catalogo es obligatorio.",
    )
    if is_active:
        _ensure_catalog_item_name_unique(
            catalog_item.catalog_type,
            normalized_name,
            exclude_id=catalog_item.id,
        )

    catalog_item.name = normalized_name
    catalog_item.description = (description or "").strip()
    catalog_item.is_active = is_active

    try:
        catalog_item.save()
    except IntegrityError as exc:
        raise ConfigValidationError(
            f"Ya existe un {_catalog_type_label(catalog_item.catalog_type)} con ese nombre.",
            field="name",
        ) from exc

    return catalog_item


@transaction.atomic
def create_academic_program(*, code, name, is_active=True):
    try:
        return AcademicProgram.objects.create(
            code=_validate_code(code),
            name=_normalize_name(name),
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un programa academico con ese codigo.") from exc


@transaction.atomic
def update_academic_program(academic_program, *, code, name, is_active):
    academic_program.code = _validate_code(code)
    academic_program.name = _normalize_name(name)
    academic_program.is_active = is_active

    try:
        academic_program.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un programa academico con ese codigo.") from exc

    return academic_program


@transaction.atomic
def create_subject(*, code, name, class_type=None, class_type_item=None, credits, weekly_hours, capacity, is_active=True):
    # Prefer explicit class_type param (legacy clients). If not provided, derive from class_type_item.
    if class_type is not None:
        normalized_class_type = _validate_class_type(class_type)
    elif class_type_item is not None:
        ct_name = (class_type_item.name or "").lower()
        if "presen" in ct_name:
            normalized_class_type = Subject.CLASS_TYPE_PRESENCIAL
        elif "virt" in ct_name:
            normalized_class_type = Subject.CLASS_TYPE_VIRTUAL
        else:
            normalized_class_type = Subject.CLASS_TYPE_PRESENCIAL
    else:
        raise ConfigValidationError("El tipo de clase es obligatorio.")
    _validate_credits_range(credits)
    _validate_weekly_hours_range(weekly_hours)
    difficulty = _calculate_difficulty(weekly_hours=weekly_hours, capacity=capacity)

    try:
        subject = Subject.objects.create(
            code=_validate_code(code),
            name=_validate_required_name(name),
            class_type=normalized_class_type,
            credits=credits,
            weekly_hours=weekly_hours,
            capacity=capacity,
            difficulty=difficulty,
            is_active=is_active,
        )
        if class_type_item is not None:
            subject.class_type_item = class_type_item
            subject.save(update_fields=["class_type_item"])
        return subject
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe una asignatura con ese codigo.") from exc


@transaction.atomic
def update_subject(subject, *, code, name, class_type=None, class_type_item=None, credits, weekly_hours, capacity, is_active):
    if class_type is not None:
        normalized_class_type = _validate_class_type(class_type)
    elif class_type_item is not None:
        ct_name = (class_type_item.name or "").lower()
        if "presen" in ct_name:
            normalized_class_type = Subject.CLASS_TYPE_PRESENCIAL
        elif "virt" in ct_name:
            normalized_class_type = Subject.CLASS_TYPE_VIRTUAL
        else:
            normalized_class_type = Subject.CLASS_TYPE_PRESENCIAL
    else:
        normalized_class_type = subject.class_type
    _validate_credits_range(credits)
    _validate_weekly_hours_range(weekly_hours)
    difficulty = _calculate_difficulty(weekly_hours=weekly_hours, capacity=capacity)

    subject.code = _validate_code(code)
    subject.name = _validate_required_name(name)
    subject.class_type = normalized_class_type
    subject.credits = credits
    subject.weekly_hours = weekly_hours
    subject.capacity = capacity
    subject.difficulty = difficulty
    subject.is_active = is_active
    if class_type_item is not None:
        subject.class_type_item = class_type_item

    try:
        subject.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe una asignatura con ese codigo.") from exc

    return subject


@transaction.atomic
def create_subject_group(*, subject, identifier, is_active=True):
    try:
        return SubjectGroup.objects.create(
            subject=subject,
            identifier=_validate_identifier(identifier),
            is_active=is_active,
        )
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un grupo con ese identificador para la asignatura.") from exc


@transaction.atomic
def update_subject_group(subject_group, *, subject, identifier, is_active):
    subject_group.subject = subject
    subject_group.identifier = _validate_identifier(identifier)
    subject_group.is_active = is_active

    try:
        subject_group.save()
    except IntegrityError as exc:
        raise ConfigValidationError("Ya existe un grupo con ese identificador para la asignatura.") from exc

    return subject_group
