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
    SpaceType,
    Subject,
    SubjectGroup,
    SubjectOffering,
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
from .services.programming_service import create_subject_offering, update_subject_offering
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
    class Meta:
        model = Subject
        fields = [
            "id",
            "code",
            "name",
            "class_type",
            "credits",
            "weekly_hours",
            "capacity",
            "difficulty",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["difficulty", "created_at", "updated_at"]

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
            "schedule_generated_at",
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


class SubjectOfferingSerializer(serializers.ModelSerializer):
    subject = SubjectSerializer(read_only=True)
    subject_group = SubjectGroupSerializer(read_only=True)
    working_day = WorkingDaySerializer(read_only=True)
    time_slot = TimeSlotSerializer(read_only=True)
    academic_period = AcademicPeriodSerializer(read_only=True)
    edit_warning = serializers.SerializerMethodField(read_only=True)
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
            "academic_program_id",
            "academic_period",
            "edit_warning",
            "semester",
            "is_active",
            "created_at",
            "updated_at",
        ]

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
            "academic_program": validated_data.get(
                "academic_program", instance.academic_program
            ),
            "academic_period": validated_data.get(
                "academic_period", instance.academic_period
            ),
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

    class Meta:
        model = Teacher
        fields = [
            "id",
            "first_name",
            "last_name",
            "email",
            "link_type",
            "link_type_id",
            "hourly_rate",
            "is_active",
        ]

    def validate_link_type_id(self, link_type):
        if link_type.catalog_type != CatalogItem.CatalogType.TEACHER_LINK_TYPE:
            raise serializers.ValidationError("El tipo de vinculacion docente no es valido.")
        return link_type


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
