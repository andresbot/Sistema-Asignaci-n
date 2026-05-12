from django.contrib.auth.models import User
from django.db import models


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Role(TimeStampedModel):
    name = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserProfile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.ForeignKey(Role, on_delete=models.PROTECT, related_name="users")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class AcademicPeriod(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    schedule_generated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-start_date"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_date__gte=models.F("start_date")),
                name="period_end_after_or_equal_start",
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Subject(TimeStampedModel):
    CLASS_TYPE_PRESENCIAL = "presencial"
    CLASS_TYPE_VIRTUAL = "virtual"
    CLASS_TYPE_CHOICES = [
        (CLASS_TYPE_PRESENCIAL, "Presencial"),
        (CLASS_TYPE_VIRTUAL, "Virtual"),
    ]
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    # Legacy static field kept for backward compatibility. New dynamic catalog field below.
    class_type = models.CharField(max_length=20, choices=CLASS_TYPE_CHOICES)
    class_type_item = models.ForeignKey(
        "CatalogItem",
        on_delete=models.PROTECT,
        related_name="subjects",
        null=True,
        blank=True,
        limit_choices_to={"catalog_type": "class_type"},
    )
    credits = models.PositiveSmallIntegerField()
    weekly_hours = models.PositiveSmallIntegerField()
    capacity = models.PositiveIntegerField()
    difficulty = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class SubjectGroup(TimeStampedModel):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="groups")
    identifier = models.CharField(max_length=80)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["subject__code", "identifier"]
        constraints = [
            models.UniqueConstraint(
                fields=["subject", "identifier"],
                name="unique_subject_group_per_subject",
            )
        ]

    def __str__(self):
        return f"{self.subject.code} - {self.identifier}"


class WorkingDay(TimeStampedModel):
    day_of_week = models.PositiveSmallIntegerField(unique=True)
    name = models.CharField(max_length=20, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["day_of_week"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(day_of_week__gte=1, day_of_week__lte=7),
                name="workingday_valid_range",
            )
        ]

    def __str__(self):
        return f"{self.day_of_week} - {self.name}"


class TimeSlot(TimeStampedModel):
    name = models.CharField(max_length=80)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(end_time__gt=models.F("start_time")),
                name="timeslot_end_after_start",
            ),
            models.UniqueConstraint(
                fields=["name", "start_time", "end_time"],
                name="unique_timeslot_name_and_range",
            ),
        ]

    def __str__(self):
        return f"{self.name} ({self.start_time}-{self.end_time})"


class SpaceType(TimeStampedModel):
    name = models.CharField(max_length=80, unique=True)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class CatalogItem(TimeStampedModel):
    class CatalogType(models.TextChoices):
        TEACHER_LINK_TYPE = "teacher_link_type", "Tipo de vinculacion docente"
        CLASS_TYPE = "class_type", "Tipo de clase"
        ACADEMIC_SPACE_TYPE = "academic_space_type", "Tipo de espacio academico"

    catalog_type = models.CharField(max_length=40, choices=CatalogType.choices)
    name = models.CharField(max_length=120)
    description = models.CharField(max_length=255, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["catalog_type", "name"]
        constraints = [
            models.UniqueConstraint(
                fields=["catalog_type", "name"],
                name="unique_catalog_item_per_type",
            )
        ]

    def __str__(self):
        return f"{self.catalog_type}: {self.name}"


class Campus(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class AcademicProgram(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name="programs")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=["campus", "name"],
                name="unique_program_name_per_campus",
            )
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Teacher(TimeStampedModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    link_type = models.ForeignKey(
        CatalogItem,
        on_delete=models.PROTECT,
        related_name="teachers",
        limit_choices_to={"catalog_type": CatalogItem.CatalogType.TEACHER_LINK_TYPE},
    )
    hourly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["last_name", "first_name"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(hourly_rate__gt=0),
                name="teacher_hourly_rate_positive",
            )
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name}".strip()


class Course(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150)
    academic_program = models.ForeignKey(
        AcademicProgram,
        on_delete=models.PROTECT,
        related_name="courses",
    )
    class_type = models.ForeignKey(
        CatalogItem,
        on_delete=models.PROTECT,
        related_name="courses",
        limit_choices_to={"catalog_type": CatalogItem.CatalogType.CLASS_TYPE},
    )
    credits = models.PositiveSmallIntegerField()
    weekly_hours = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.CheckConstraint(check=models.Q(credits__gt=0), name="course_credits_positive"),
            models.CheckConstraint(
                check=models.Q(weekly_hours__gt=0),
                name="course_weekly_hours_positive",
            ),
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class CourseGroup(TimeStampedModel):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="groups")
    identifier = models.CharField(max_length=30)
    student_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["course_id", "identifier"]
        constraints = [
            models.UniqueConstraint(
                fields=["course", "identifier"],
                name="unique_group_identifier_per_course",
            )
        ]

    def __str__(self):
        return f"{self.course.code} - {self.identifier}"


class Classroom(TimeStampedModel):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=120)
    campus = models.ForeignKey(Campus, on_delete=models.PROTECT, related_name="classrooms")
    space_type = models.ForeignKey(
        CatalogItem,
        on_delete=models.PROTECT,
        related_name="classrooms",
        limit_choices_to={"catalog_type": CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE},
    )
    capacity = models.PositiveIntegerField()
    is_accessible = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["code"]
        constraints = [
            models.CheckConstraint(check=models.Q(capacity__gt=0), name="classroom_capacity_positive")
        ]

    def __str__(self):
        return f"{self.code} - {self.name}"


class SubjectOffering(TimeStampedModel):
    subject = models.ForeignKey(Subject, on_delete=models.PROTECT, related_name="offerings")
    subject_group = models.ForeignKey(
        SubjectGroup,
        on_delete=models.PROTECT,
        related_name="subject_offerings",
        null=True,
        blank=True,
    )
    working_day = models.ForeignKey(
        "WorkingDay",
        on_delete=models.PROTECT,
        related_name="subject_offerings",
        null=True,
        blank=True,
    )
    time_slot = models.ForeignKey(
        "TimeSlot",
        on_delete=models.PROTECT,
        related_name="subject_offerings",
        null=True,
        blank=True,
    )
    required_space_type = models.ForeignKey(
        "CatalogItem",
        on_delete=models.PROTECT,
        related_name="subject_offerings",
        null=True,
        blank=True,
        limit_choices_to={"catalog_type": "academic_space_type"},
    )
    teacher = models.ForeignKey(
        "Teacher",
        on_delete=models.SET_NULL,
        related_name="subject_offerings",
        null=True,
        blank=True,
    )
    student_count = models.PositiveIntegerField(null=True, blank=True)
    academic_program = models.ForeignKey(
        AcademicProgram, on_delete=models.PROTECT, related_name="subject_offerings"
    )
    academic_period = models.ForeignKey(
        AcademicPeriod, on_delete=models.PROTECT, related_name="subject_offerings"
    )
    semester = models.PositiveSmallIntegerField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["academic_period", "semester", "subject__code", "subject_group__identifier"]
        constraints = [
            models.CheckConstraint(
                check=models.Q(semester__gte=1),
                name="subject_offering_valid_semester",
            ),
            models.UniqueConstraint(
                fields=["academic_period", "subject_group", "academic_program", "semester"],
                name="unique_subject_offering_per_period_program_group_semester",
            ),
        ]

    def __str__(self):
        group_label = self.subject_group.identifier if self.subject_group else "Sin grupo"
        day_label = self.working_day.name if self.working_day else "Sin dia"
        slot_label = self.time_slot.name if self.time_slot else "Sin franja"
        return (
            f"{self.subject.code} | {group_label} | {self.academic_program.code} | "
            f"{day_label} | {slot_label} | S{self.semester}"
        )
