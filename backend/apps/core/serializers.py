from django.contrib.auth import authenticate
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken

from .models import (
    AcademicPeriod,
    AcademicProgram,
    Campus,
    CatalogItem,
    Classroom,
    Course,
    CourseGroup,
    Role,
    ScheduleExecution,
    SpaceType,
    Subject,
    SubjectGroup,
    SubjectOffering,
    StudentEnrollment,
    Teacher,
    TimeSlot,
    UserProfile,
    WorkingDay,
)
from .permissions import get_user_role_name
from .services.config_service import (
    ConfigValidationError,
    create_academic_period,
    create_catalog_item,
    create_space_type,
    create_subject,
    create_subject_group,
    create_time_slot,
    create_working_day,
    update_academic_period,
    update_catalog_item,
    update_space_type,
    update_subject,
    update_subject_group,
    update_time_slot,
    update_working_day,
)
from .services.programming_service import (
    create_subject_offering,
    get_offering_non_assignable_reason,
    update_subject_offering,
)
from .services.user_service import (
    UserEmailAlreadyExistsError,
    create_user_with_profile,
    update_user_profile,
)


def _raise_config_validation_error(exc, default_field):
    field = exc.field or default_field
    raise serializers.ValidationError({field: str(exc)}) from exc


class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, trim_whitespace=False)

    def validate(self, attrs):
        request = self.context.get("request")
        email = attrs.get("email")
        password = attrs.get("password")

        user = authenticate(request=request, username=email, password=password)
        if user is None:
            raise serializers.ValidationError("Credenciales invalidas.")

        refresh = RefreshToken.for_user(user)
        role_name = get_user_role_name(user)

        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "role": role_name,
                "is_superuser": user.is_superuser,
            },
        }


class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ["id", "name", "description", "is_active"]


class SubjectSerializer(serializers.ModelSerializer):
    # expose dynamic catalog item id for class type and keep legacy string for read
    # allow legacy `class_type` in input but make it optional (clients may send
    # either `class_type` or `class_type_item_id`).
    class_type = serializers.CharField(required=False, allow_null=True)
    class_type_item = serializers.SerializerMethodField(read_only=True)
    class_type_item_id = serializers.PrimaryKeyRelatedField(
        source="class_type_item",
        queryset=CatalogItem.objects.filter(catalog_type=CatalogItem.CatalogType.CLASS_TYPE),
        write_only=True,
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name",
            "class_type",           # legacy read
            "class_type_item",
            "class_type_item_id",  # write
            "credits",
            "weekly_hours",
            "capacity",
            "difficulty",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["difficulty", "created_at", "updated_at"]

    def get_class_type_item(self, obj):
        item = getattr(obj, "class_type_item", None)
        if not item:
            return None
        return {"id": item.id, "name": item.name, "is_active": item.is_active}

    @staticmethod
    def _map_subject_error(message):
        normalized_message = str(message).lower()

        if "codigo" in normalized_message:
            return {"code": str(message)}
        if "nombre" in normalized_message:
            return {"name": str(message)}
        if "tipo de clase" in normalized_message:
            return {"class_type": str(message)}
        if "creditos" in normalized_message:
            return {"credits": str(message)}
        if "intensidad" in normalized_message:
            return {"weekly_hours": str(message)}
        if "cupo" in normalized_message:
            return {"capacity": str(message)}

        return {"non_field_errors": [str(message)]}

    def create(self, validated_data):
        try:
            return create_subject(**validated_data)
        except ConfigValidationError as exc:
            raise serializers.ValidationError(self._map_subject_error(exc)) from exc

    def update(self, instance, validated_data):
        payload = {
            "code": validated_data.get("code", instance.code),
            "name": validated_data.get("name", instance.name),
            "class_type": validated_data.get("class_type", instance.class_type),
            "credits": validated_data.get("credits", instance.credits),
            "weekly_hours": validated_data.get("weekly_hours", instance.weekly_hours),
            "capacity": validated_data.get("capacity", instance.capacity),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_subject(instance, **payload)
        except ConfigValidationError as exc:
            raise serializers.ValidationError(self._map_subject_error(exc)) from exc


class SubjectGroupSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_id = serializers.PrimaryKeyRelatedField(
        source="subject", queryset=Subject.objects.all(), write_only=True
    )

    class Meta:
        model = SubjectGroup
        fields = [
            "id",
            "subject",
            "subject_id",
            "identifier",
            "is_active",
            "created_at",
            "updated_at",
        ]
        validators = []

    def validate(self, attrs):
        subject = attrs.get("subject", getattr(self.instance, "subject", None))
        identifier = attrs.get("identifier", getattr(self.instance, "identifier", None))

        if subject and identifier:
            duplicated_group = SubjectGroup.objects.filter(
                subject=subject,
                identifier=identifier.strip(),
            )

            if self.instance is not None:
                duplicated_group = duplicated_group.exclude(id=self.instance.id)

            if duplicated_group.exists():
                raise serializers.ValidationError(
                    {
                        "identifier": "Ya existe un grupo con ese identificador para la asignatura.",
                    }
                )

        return attrs

    def create(self, validated_data):
        try:
            return create_subject_group(**validated_data)
        except ConfigValidationError as exc:
            raise serializers.ValidationError({"identifier": str(exc)}) from exc

    def update(self, instance, validated_data):
        payload = {
            "subject": validated_data.get("subject", instance.subject),
            "identifier": validated_data.get("identifier", instance.identifier),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_subject_group(instance, **payload)
        except ConfigValidationError as exc:
            raise serializers.ValidationError({"identifier": str(exc)}) from exc


class UserProfileReadSerializer(serializers.ModelSerializer):
    role = RoleSerializer(read_only=True)
    user_id = serializers.IntegerField(source="user.id", read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            "id",
            "user_id",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "role",
            "created_at",
            "updated_at",
        ]


class UserCreateSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=8, trim_whitespace=False)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    role_id = serializers.PrimaryKeyRelatedField(source="role", queryset=Role.objects.all())

    def create(self, validated_data):
        try:
            return create_user_with_profile(**validated_data)
        except UserEmailAlreadyExistsError as exc:
            raise serializers.ValidationError({"email": str(exc)}) from exc


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False)
    first_name = serializers.CharField(max_length=100, required=False)
    last_name = serializers.CharField(max_length=100, required=False)
    role_id = serializers.PrimaryKeyRelatedField(
        source="role", queryset=Role.objects.all(), required=False
    )
    is_active = serializers.BooleanField(required=False)

    def update(self, instance, validated_data):
        payload = {
            "email": validated_data.get("email", instance.email),
            "first_name": validated_data.get("first_name", instance.first_name),
            "last_name": validated_data.get("last_name", instance.last_name),
            "role": validated_data.get("role", instance.role),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_user_profile(instance, **payload)
        except UserEmailAlreadyExistsError as exc:
            raise serializers.ValidationError({"email": str(exc)}) from exc


class AcademicPeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicPeriod
        fields = [
            "id",
            "code",
            "name",
            "start_date",
            "end_date",
            "is_active",
            "is_schedule_published",
            "schedule_generated_at",
            "schedule_published_at",
        ]

    def create(self, validated_data):
        try:
            return create_academic_period(**validated_data)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="code")

    def update(self, instance, validated_data):
        payload = {
            "code": validated_data.get("code", instance.code),
            "name": validated_data.get("name", instance.name),
            "start_date": validated_data.get("start_date", instance.start_date),
            "end_date": validated_data.get("end_date", instance.end_date),
            "is_active": validated_data.get("is_active", instance.is_active),
            "is_schedule_published": validated_data.get(
                "is_schedule_published", instance.is_schedule_published
            ),
        }

        try:
            return update_academic_period(instance, **payload)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="code")


class WorkingDaySerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkingDay
        fields = ["id", "day_of_week", "name", "is_active"]

    def create(self, validated_data):
        try:
            return create_working_day(**validated_data)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="day_of_week")

    def update(self, instance, validated_data):
        payload = {
            "day_of_week": validated_data.get("day_of_week", instance.day_of_week),
            "name": validated_data.get("name", instance.name),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_working_day(instance, **payload)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="day_of_week")


class TimeSlotSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeSlot
        fields = ["id", "name", "start_time", "end_time", "is_active"]

    def create(self, validated_data):
        try:
            return create_time_slot(**validated_data)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="end_time")

    def update(self, instance, validated_data):
        payload = {
            "name": validated_data.get("name", instance.name),
            "start_time": validated_data.get("start_time", instance.start_time),
            "end_time": validated_data.get("end_time", instance.end_time),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_time_slot(instance, **payload)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="end_time")


class SpaceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpaceType
        fields = ["id", "name", "description", "is_active"]

    def create(self, validated_data):
        try:
            return create_space_type(**validated_data)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="name")

    def update(self, instance, validated_data):
        payload = {
            "name": validated_data.get("name", instance.name),
            "description": validated_data.get("description", instance.description),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_space_type(instance, **payload)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="name")


class CatalogItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CatalogItem
        fields = ["id", "catalog_type", "name", "description", "is_active"]
        read_only_fields = ["catalog_type"]

    def create(self, validated_data):
        catalog_type = self.context.get("catalog_type")
        try:
            return create_catalog_item(catalog_type=catalog_type, **validated_data)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="name")

    def update(self, instance, validated_data):
        payload = {
            "name": validated_data.get("name", instance.name),
            "description": validated_data.get("description", instance.description),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_catalog_item(instance, **payload)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="name")


class TeacherSummarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ["id", "first_name", "last_name", "email", "is_active"]


class SubjectOfferingSerializer(serializers.ModelSerializer):
    subject_name = serializers.CharField(source="subject.name", read_only=True)
    day = serializers.CharField(source="working_day.name", read_only=True)
    start_time = serializers.TimeField(source="time_slot.start_time", read_only=True)
    end_time = serializers.TimeField(source="time_slot.end_time", read_only=True)
    campus = serializers.CharField(source="assigned_classroom.campus.name", read_only=True)
    classroom_code = serializers.CharField(source="assigned_classroom.code", read_only=True)
    subject = SubjectSerializer(read_only=True)
    subject_group = SubjectGroupSerializer(read_only=True)
    working_day = WorkingDaySerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    required_space_type = CatalogItemSerializer(read_only=True)
    teacher = TeacherSummarySerializer(read_only=True)
    academic_period = AcademicPeriodSerializer(read_only=True)
    edit_warning = serializers.SerializerMethodField(read_only=True)
    non_assignable_reason = serializers.SerializerMethodField(read_only=True)
    requires_accessible_classroom = serializers.BooleanField(required=False)
    subject_id = serializers.PrimaryKeyRelatedField(
        source="subject", queryset=Subject.objects.all(), write_only=True
    )
    subject_group_id = serializers.PrimaryKeyRelatedField(
        source="subject_group", queryset=SubjectGroup.objects.select_related("subject").all(), write_only=True
    )
    working_day_id = serializers.PrimaryKeyRelatedField(
        source="working_day", queryset=WorkingDay.objects.all(), write_only=True
    )
    time_slot_id = serializers.PrimaryKeyRelatedField(
        source="time_slot", queryset=TimeSlot.objects.all(), write_only=True
    )
    required_space_type_id = serializers.PrimaryKeyRelatedField(
        source="required_space_type",
        queryset=CatalogItem.objects.filter(catalog_type=CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE),
        write_only=True,
        required=False,
        allow_null=True,
    )
    teacher_id = serializers.PrimaryKeyRelatedField(
        source="teacher",
        queryset=Teacher.objects.filter(is_active=True),
        write_only=True,
        required=False,
        allow_null=True,
    )
    academic_program_id = serializers.PrimaryKeyRelatedField(
        source="academic_program", queryset=AcademicProgram.objects.all(), write_only=True
    )

    class Meta:
        model = SubjectOffering
        fields = [
            "id",
            "subject",
            "subject_id",
            "subject_group",
            "subject_group_id",
            "working_day",
            "working_day_id",
            "time_slot",
            "time_slot_id",
            "required_space_type",
            "required_space_type_id",
            "teacher",
            "teacher_id",
            "requires_accessible_classroom",
            "student_count",
            "non_assignable_reason",
            "academic_program_id",
            "academic_period",
            "edit_warning",
            "semester",
            "is_active",
            "created_at",
            "updated_at",
            # Campos agregados para la historia de usuario
            "subject_name",
            "day",
            "start_time",
            "end_time",
            "campus",
            "classroom_code",
        ]

    def validate_required_space_type_id(self, value):
        if value is not None and value.catalog_type != CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE:
            raise serializers.ValidationError("El tipo de espacio debe ser del catalogo de espacios academicos.")
        return value

    def create(self, validated_data):
        try:
            return create_subject_offering(**validated_data)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="subject_group_id")

    def update(self, instance, validated_data):
        payload = {
            "subject": validated_data.get("subject", instance.subject),
            "subject_group": validated_data.get("subject_group", instance.subject_group),
            "working_day": validated_data.get("working_day", instance.working_day),
            "time_slot": validated_data.get("time_slot", instance.time_slot),
            "required_space_type": validated_data.get("required_space_type", instance.required_space_type),
            "teacher": validated_data.get("teacher", instance.teacher),
            "requires_accessible_classroom": validated_data.get(
                "requires_accessible_classroom", instance.requires_accessible_classroom
            ),
            "student_count": validated_data.get("student_count", instance.student_count),
            "academic_program": validated_data.get("academic_program", instance.academic_program),
            "academic_period": validated_data.get("academic_period", instance.academic_period),
            "semester": validated_data.get("semester", instance.semester),
            "is_active": validated_data.get("is_active", instance.is_active),
        }

        try:
            return update_subject_offering(instance, **payload)
        except ConfigValidationError as exc:
            _raise_config_validation_error(exc, default_field="subject_group_id")

    def get_edit_warning(self, obj):
        """Return a warning message if the academic period has a generated schedule."""
        period = getattr(obj, "academic_period", None)
        if not period:
            return None
        timestamp = getattr(period, "schedule_generated_at", None)
        if not timestamp:
            return None
        try:
            return (
                f"⚠️ El horario para este período fue generado el {timestamp.strftime('%Y-%m-%d %H:%M')}. "
                "Si realiza cambios, el horario deberá regenerarse."
            )
        except Exception:
            return "⚠️ El horario para este período ya fue generado. Si realiza cambios, deberá regenerarse."

    def get_non_assignable_reason(self, obj):
        return get_offering_non_assignable_reason(obj)


class CampusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Campus
        fields = ["id", "code", "name", "is_active"]


class AcademicProgramSerializer(serializers.ModelSerializer):
    campus = CampusSerializer(read_only=True)
    campus_id = serializers.PrimaryKeyRelatedField(source="campus", queryset=Campus.objects.all())

    class Meta:
        model = AcademicProgram
        fields = ["id", "code", "name", "campus", "campus_id", "is_active"]


class TeacherSerializer(serializers.ModelSerializer):
    link_type = CatalogItemSerializer(read_only=True)
    link_type_id = serializers.PrimaryKeyRelatedField(source="link_type", queryset=CatalogItem.objects.all())
    user_profile_id = serializers.PrimaryKeyRelatedField(
        source="user_profile",
        queryset=UserProfile.objects.select_related("role").all(),
        required=False,
        allow_null=True,
        write_only=True,
    )
    user_profile = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Teacher
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "user_profile",
            "user_profile_id",
            "link_type",
            "link_type_id",
            "hourly_rate",
            "is_active",
        ]

    def validate_link_type_id(self, link_type):
        if link_type.catalog_type != CatalogItem.CatalogType.TEACHER_LINK_TYPE:
            raise serializers.ValidationError("El tipo de vinculacion docente no es valido.")
        return link_type

    def get_user_profile(self, obj):
        profile = getattr(obj, "user_profile", None)
        if not profile:
            return None
        return {
            "id": profile.id,
            "email": profile.email,
            "first_name": profile.first_name,
            "last_name": profile.last_name,
            "role": profile.role.name if profile.role else None,
        }


class StudentEnrollmentSerializer(serializers.ModelSerializer):
    student = UserProfileReadSerializer(read_only=True)
    student_id = serializers.PrimaryKeyRelatedField(
        source="student",
        queryset=UserProfile.objects.select_related("role").all(),
        write_only=True,
    )
    subject_offering = SubjectOfferingSerializer(read_only=True)
    subject_offering_id = serializers.PrimaryKeyRelatedField(
        source="subject_offering",
        queryset=SubjectOffering.objects.select_related("academic_period").all(),
        write_only=True,
    )

    class Meta:
        model = StudentEnrollment
        fields = [
            "id",
            "student",
            "student_id",
            "subject_offering",
            "subject_offering_id",
            "is_active",
            "created_at",
            "updated_at",
        ]

    def validate_student_id(self, student):
        if not student.role or student.role.name.strip().lower() != "estudiante":
            raise serializers.ValidationError("La cuenta seleccionada no tiene rol de estudiante.")
        return student

    def validate(self, attrs):
        student = attrs.get("student", getattr(self.instance, "student", None))
        subject_offering = attrs.get("subject_offering", getattr(self.instance, "subject_offering", None))

        if student and subject_offering:
            duplicate = StudentEnrollment.objects.filter(student=student, subject_offering=subject_offering)
            if self.instance is not None:
                duplicate = duplicate.exclude(id=self.instance.id)
            if duplicate.exists():
                raise serializers.ValidationError(
                    {"non_field_errors": ["Ya existe una matricula para este estudiante y horario."]}
                )

        return attrs


class CourseSerializer(serializers.ModelSerializer):
    academic_program = AcademicProgramSerializer(read_only=True)
    academic_program_id = serializers.PrimaryKeyRelatedField(
        source="academic_program",
        queryset=AcademicProgram.objects.all(),
    )
    class_type = CatalogItemSerializer(read_only=True)
    class_type_id = serializers.PrimaryKeyRelatedField(source="class_type", queryset=CatalogItem.objects.all())

    class Meta:
        model = Course
        fields = [
            "id",
            "code",
            "name",
            "academic_program",
            "academic_program_id",
            "class_type",
            "class_type_id",
            "credits",
            "weekly_hours",
            "is_active",
        ]

    def validate_class_type_id(self, class_type):
        if class_type.catalog_type != CatalogItem.CatalogType.CLASS_TYPE:
            raise serializers.ValidationError("El tipo de clase no es valido.")
        return class_type


class CourseGroupSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)
    course_id = serializers.PrimaryKeyRelatedField(source="course", queryset=Course.objects.all())

    class Meta:
        model = CourseGroup
        fields = ["id", "course", "course_id", "identifier", "student_count", "is_active"]


class ClassroomSerializer(serializers.ModelSerializer):
    campus = CampusSerializer(read_only=True)
    campus_id = serializers.PrimaryKeyRelatedField(source="campus", queryset=Campus.objects.all())
    space_type = CatalogItemSerializer(read_only=True)
    space_type_id = serializers.PrimaryKeyRelatedField(source="space_type", queryset=CatalogItem.objects.all())

    class Meta:
        model = Classroom
        fields = [
            "id",
            "code",
            "name",
            "campus",
            "campus_id",
            "space_type",
            "space_type_id",
            "capacity",
            "is_accessible",
            "is_active",
        ]

    def validate_space_type_id(self, space_type):
        if space_type.catalog_type != CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE:
            raise serializers.ValidationError("El tipo de espacio academico no es valido.")
        return space_type

    def validate_capacity(self, value):
        if value <= 0:
            raise serializers.ValidationError("La capacidad debe ser mayor a cero.")
        return value


class HorarioOfferingSerializer(serializers.ModelSerializer):
    """Serializer simplificado para la grilla de horario del administrador."""

    working_day = WorkingDaySerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    asignatura = serializers.SerializerMethodField()
    docente = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField()
    espacio = serializers.SerializerMethodField()

    class Meta:
        model = SubjectOffering
        fields = ["id", "working_day", "time_slot", "asignatura", "docente", "grupo", "espacio"]

    def get_asignatura(self, obj):
        return {"id": obj.subject.id, "code": obj.subject.code, "name": obj.subject.name}

    def get_docente(self, obj):
        if not obj.teacher:
            return None
        return {
            "id": obj.teacher.id,
            "first_name": obj.teacher.first_name,
            "last_name": obj.teacher.last_name,
        }

    def get_grupo(self, obj):
        if not obj.subject_group:
            return None
        return {"id": obj.subject_group.id, "name": obj.subject_group.identifier}

    def get_espacio(self, obj):
        if not obj.assigned_classroom:
            return None
        campus = obj.assigned_classroom.campus
        return {
            "id": obj.assigned_classroom.id,
            "name": obj.assigned_classroom.name,
            "sede": {"id": campus.id, "name": campus.name} if campus else None,
        }


class HorarioUnassignedSerializer(serializers.ModelSerializer):
    """Serializer para asignaturas que el algoritmo no pudo programar."""

    asignatura = serializers.SerializerMethodField()
    grupo = serializers.SerializerMethodField()
    razon = serializers.SerializerMethodField()

    class Meta:
        model = SubjectOffering
        fields = ["id", "asignatura", "grupo", "razon"]

    def get_asignatura(self, obj):
        return {"id": obj.subject.id, "code": obj.subject.code, "name": obj.subject.name}

    def get_grupo(self, obj):
        if not obj.subject_group:
            return {"id": None, "name": "Sin grupo"}
        return {"id": obj.subject_group.id, "name": obj.subject_group.identifier}

    def get_razon(self, obj):
        if obj.schedule_failure_reason:
            return obj.schedule_failure_reason
        from .services.programming_service import get_offering_non_assignable_reason
        return get_offering_non_assignable_reason(obj) or "Razon no especificada."


class MyScheduleSerializer(serializers.ModelSerializer):
    """Serializer para la vista de horario personal de docentes y estudiantes."""

    working_day = WorkingDaySerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    subject = serializers.SerializerMethodField()
    subject_group = serializers.SerializerMethodField()
    academic_program = serializers.SerializerMethodField()
    teacher = serializers.SerializerMethodField()
    sede = serializers.SerializerMethodField()
    salon = serializers.SerializerMethodField()

    class Meta:
        model = SubjectOffering
        fields = [
            "id", "subject", "subject_group", "working_day", "time_slot",
            "academic_program", "teacher", "semester", "sede", "salon",
        ]

    def get_subject(self, obj):
        return {"id": obj.subject.id, "code": obj.subject.code, "name": obj.subject.name}

    def get_subject_group(self, obj):
        if not obj.subject_group:
            return None
        return {"id": obj.subject_group.id, "identifier": obj.subject_group.identifier}

    def get_academic_program(self, obj):
        if not obj.academic_program:
            return None
        return {
            "id": obj.academic_program.id,
            "code": obj.academic_program.code,
            "name": obj.academic_program.name,
        }

    def get_teacher(self, obj):
        if not obj.teacher:
            return None
        return {
            "id": obj.teacher.id,
            "first_name": obj.teacher.first_name,
            "last_name": obj.teacher.last_name,
        }

    def get_sede(self, obj):
        if not obj.assigned_classroom or not obj.assigned_classroom.campus:
            return None
        return obj.assigned_classroom.campus.name

    def get_salon(self, obj):
        if not obj.assigned_classroom:
            return None
        return obj.assigned_classroom.name


class ScheduleExecutionSerializer(serializers.ModelSerializer):
    academic_period = AcademicPeriodSerializer(read_only=True)
    requested_by_username = serializers.CharField(source="requested_by.username", read_only=True)

    class Meta:
        model = ScheduleExecution
        fields = [
            "id",
            "academic_period",
            "requested_by_username",
            "status",
            "progress",
            "parameters",
            "result_snapshot",
            "error_message",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
        ]
        read_only_fields = [
            "status",
            "progress",
            "result_snapshot",
            "error_message",
            "started_at",
            "finished_at",
            "created_at",
            "updated_at",
            "requested_by_username",
        ]


class ScheduleExecutionCreateSerializer(serializers.Serializer):
    academic_period_id = serializers.PrimaryKeyRelatedField(
        source="academic_period",
        queryset=AcademicPeriod.objects.all(),
    )
    poblacion_size = serializers.IntegerField(min_value=1, required=False, default=20)
    generaciones = serializers.IntegerField(min_value=1, required=False, default=200)
    proporcion_heuristica = serializers.FloatField(min_value=0, max_value=1, required=False, default=0.2)
    estancamiento_max = serializers.IntegerField(min_value=0, required=False, default=10)

    def validate(self, attrs):
        return attrs
