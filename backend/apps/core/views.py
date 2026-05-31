from django.db import transaction
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
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
from .services.health_service import build_health_payload
from .permissions import HasAllowedRoles, get_user_role_name
from .serializers import (
    AcademicPeriodSerializer,
    AcademicProgramSerializer,
    CampusSerializer,
    CatalogItemSerializer,
    ClassroomSerializer,
    CourseGroupSerializer,
    CourseSerializer,
    HorarioOfferingSerializer,
    HorarioUnassignedSerializer,
    LoginSerializer,
    MyScheduleSerializer,
    RoleSerializer,
    ScheduleExecutionCreateSerializer,
    ScheduleExecutionSerializer,
    SpaceTypeSerializer,
    SubjectGroupSerializer,
    SubjectOfferingSerializer,
    SubjectSerializer,
    StudentEnrollmentSerializer,
    TeacherSerializer,
    TimeSlotSerializer,
    UserCreateSerializer,
    UserProfileReadSerializer,
    UserUpdateSerializer,
    WorkingDaySerializer,
)
from .services.master_data_import_service import (
    MasterDataImportError,
    get_import_templates,
    import_master_data,
)
from .services.config_service import publish_academic_period, unpublish_academic_period
from .services.schedule_validation_service import validate_schedule_before_execution
from .services.schedule_execution_service import queue_schedule_execution
from .services.user_service import deactivate_user_profile
from .services.programming_service import get_active_academic_period


@api_view(["GET"])
def health_check(_request):
    return Response(build_health_payload())


class LoginAPIView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        return Response(serializer.validated_data)


class LogoutAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            raise ValidationError("Se requiere el refresh token para cerrar sesion.")

        try:
            RefreshToken(refresh_token).blacklist()
        except TokenError as exc:
            raise ValidationError("Refresh token invalido o expirado.") from exc

        return Response(status=204)


class MeAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        role_name = get_user_role_name(request.user)
        profile = getattr(request.user, "profile", None)

        return Response(
            {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "first_name": request.user.first_name,
                "last_name": request.user.last_name,
                "role": role_name,
                "is_superuser": request.user.is_superuser,
                "profile": {
                    "id": profile.id if profile else None,
                    "is_active": profile.is_active if profile else None,
                },
            }
        )


class AdminOnlyAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAllowedRoles]
    allowed_roles = ("administrador",)

    def get(self, request):
        return Response(
            {
                "message": "Acceso validado para administradores.",
                "role": get_user_role_name(request.user),
            }
        )


class AdminProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAllowedRoles]
    allowed_roles = ("administrador",)


class CoordinatorProtectedAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAllowedRoles]
    allowed_roles = ("administrador", "coordinador")


def _ensure_admin_role(user):
    role_name = get_user_role_name(user)
    if not (user.is_superuser or role_name == "administrador"):
        raise PermissionDenied("Solo administradores pueden modificar catalogos.")


def _validate_catalog_type_or_404(catalog_type):
    valid_types = {choice for choice, _label in CatalogItem.CatalogType.choices}
    if catalog_type not in valid_types:
        raise ValidationError("Tipo de catalogo invalido.")


class RoleListAPIView(AdminProtectedAPIView):
    def get(self, _request):
        queryset = Role.objects.filter(is_active=True).order_by("name")
        serializer = RoleSerializer(queryset, many=True)
        return Response(serializer.data)


class UserListCreateAPIView(AdminProtectedAPIView):
    def get(self, request):
        queryset = UserProfile.objects.select_related("role", "user").order_by(
            "last_name", "first_name"
        )

        role_id = request.query_params.get("role_id")
        is_active = request.query_params.get("is_active")
        search = request.query_params.get("search")

        if role_id:
            queryset = queryset.filter(role_id=role_id)

        if is_active is not None:
            normalized_value = is_active.strip().lower()
            if normalized_value in ("true", "1"):
                queryset = queryset.filter(is_active=True)
            elif normalized_value in ("false", "0"):
                queryset = queryset.filter(is_active=False)

        if search:
            queryset = queryset.filter(
                Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        serializer = UserProfileReadSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        profile = serializer.save()
        response_serializer = UserProfileReadSerializer(profile)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class UserDetailAPIView(AdminProtectedAPIView):
    def get_object(self, user_profile_id):
        return get_object_or_404(
            UserProfile.objects.select_related("role", "user"),
            id=user_profile_id,
        )

    def patch(self, request, user_profile_id):
        profile = self.get_object(user_profile_id)
        serializer = UserUpdateSerializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_profile = serializer.save()
        response_serializer = UserProfileReadSerializer(updated_profile)
        return Response(response_serializer.data)

    def delete(self, _request, user_profile_id):
        profile = self.get_object(user_profile_id)
        deactivate_user_profile(profile)
        return Response(status=status.HTTP_204_NO_CONTENT)


class ConfigListCreateBaseAPIView(AdminProtectedAPIView):
    queryset = None
    serializer_class = None

    def get(self, _request):
        serializer = self.serializer_class(self.queryset.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ConfigDetailBaseAPIView(AdminProtectedAPIView):
    queryset = None
    serializer_class = None

    def get_object(self, config_id):
        return get_object_or_404(self.queryset, id=config_id)

    def patch(self, request, config_id):
        instance = self.get_object(config_id)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        response_serializer = self.serializer_class(updated_instance)
        return Response(response_serializer.data)

    def delete(self, _request, config_id):
        instance = self.get_object(config_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CoordinatorReadableConfigListCreateAPIView(CoordinatorProtectedAPIView):
    queryset = None
    serializer_class = None

    def get(self, _request):
        serializer = self.serializer_class(self.queryset.all(), many=True)
        return Response(serializer.data)

    def post(self, request):
        if get_user_role_name(request.user) != "administrador":
            raise PermissionDenied("Solo administradores pueden crear en este catalogo.")

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


def _filter_by_is_active_param(queryset, request):
    is_active = request.query_params.get("is_active")
    if is_active is None:
        return queryset

    normalized_value = is_active.strip().lower()
    if normalized_value in ("true", "1"):
        return queryset.filter(is_active=True)
    if normalized_value in ("false", "0"):
        return queryset.filter(is_active=False)
    return queryset


class MasterDataListCreateBaseAPIView(AdminProtectedAPIView):
    queryset = None
    serializer_class = None

    def get_queryset(self, request):
        queryset = self.queryset.all()
        queryset = _filter_by_is_active_param(queryset, request)

        search = request.query_params.get("search")
        if search:
            queryset = self.apply_search_filter(queryset, search)

        return self.apply_extra_filters(queryset, request)

    def apply_search_filter(self, queryset, search):
        return queryset

    def apply_extra_filters(self, queryset, request):
        return queryset

    def get(self, request):
        serializer = self.serializer_class(self.get_queryset(request), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = self.serializer_class(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class MasterDataDetailBaseAPIView(AdminProtectedAPIView):
    queryset = None
    serializer_class = None

    def get_object(self, item_id):
        return get_object_or_404(self.queryset, id=item_id)

    def patch(self, request, item_id):
        instance = self.get_object(item_id)
        serializer = self.serializer_class(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        response_serializer = self.serializer_class(updated_instance)
        return Response(response_serializer.data)

    def delete(self, _request, item_id):
        instance = self.get_object(item_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AcademicPeriodListCreateAPIView(ConfigListCreateBaseAPIView):
    queryset = AcademicPeriod.objects.order_by("-start_date")
    serializer_class = AcademicPeriodSerializer


class AcademicPeriodDetailAPIView(ConfigDetailBaseAPIView):
    queryset = AcademicPeriod.objects.all()
    serializer_class = AcademicPeriodSerializer


def _get_pending_subject_offerings_for_period(academic_period):
    return SubjectOffering.objects.select_related(
        "subject",
        "subject_group",
        "working_day",
        "time_slot",
        "academic_program",
        "academic_period",
    ).filter(
        academic_period=academic_period,
        is_active=True,
        assigned_classroom__isnull=True,
    ).order_by("subject__code", "subject_group__identifier", "semester", "id")


class AcademicPeriodPublishAPIView(AdminProtectedAPIView):
    def post(self, request, config_id):
        academic_period = get_object_or_404(AcademicPeriod, id=config_id)
        force_value = request.data.get("force", False)
        force_publish = str(force_value).strip().lower() in ("true", "1", "yes", "on")

        pending_queryset = _get_pending_subject_offerings_for_period(academic_period)
        pending_items = HorarioUnassignedSerializer(pending_queryset, many=True).data

        if pending_items and not force_publish:
            return Response(
                {
                    "published": False,
                    "confirmation_required": True,
                    "warning": "Existen asignaturas sin salon asignado. Puede publicarse de todos modos si confirma.",
                    "pending_offerings": pending_items,
                    "academic_period": AcademicPeriodSerializer(academic_period).data,
                },
                status=status.HTTP_200_OK,
            )

        publish_academic_period(academic_period)
        return Response(
            {
                "published": True,
                "confirmation_required": False,
                "warning": None,
                "pending_offerings": pending_items,
                "academic_period": AcademicPeriodSerializer(academic_period).data,
            },
            status=status.HTTP_200_OK,
        )


class AcademicPeriodUnpublishAPIView(AdminProtectedAPIView):
    def post(self, request, config_id):
        academic_period = get_object_or_404(AcademicPeriod, id=config_id)
        unpublish_academic_period(academic_period)
        return Response(
            {
                "published": False,
                "academic_period": AcademicPeriodSerializer(academic_period).data,
            },
            status=status.HTTP_200_OK,
        )


class ScheduleAcademicPeriodListAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, _request):
        queryset = AcademicPeriod.objects.filter(is_active=True).order_by("-start_date", "-id")
        serializer = AcademicPeriodSerializer(queryset, many=True)
        return Response(serializer.data)


class WorkingDayListCreateAPIView(CoordinatorReadableConfigListCreateAPIView):
    queryset = WorkingDay.objects.order_by("day_of_week")
    serializer_class = WorkingDaySerializer


class WorkingDayDetailAPIView(ConfigDetailBaseAPIView):
    queryset = WorkingDay.objects.all()
    serializer_class = WorkingDaySerializer


class TimeSlotListCreateAPIView(CoordinatorReadableConfigListCreateAPIView):
    queryset = TimeSlot.objects.order_by("start_time")
    serializer_class = TimeSlotSerializer


class TimeSlotDetailAPIView(ConfigDetailBaseAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class SpaceTypeListCreateAPIView(ConfigListCreateBaseAPIView):
    queryset = SpaceType.objects.order_by("name")
    serializer_class = SpaceTypeSerializer


class SpaceTypeDetailAPIView(ConfigDetailBaseAPIView):
    queryset = SpaceType.objects.all()
    serializer_class = SpaceTypeSerializer


class CatalogItemListCreateAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, catalog_type):
        _validate_catalog_type_or_404(catalog_type)
        queryset = CatalogItem.objects.filter(catalog_type=catalog_type).order_by("name")

        is_active = request.query_params.get("is_active")
        if is_active is not None:
            normalized_value = is_active.strip().lower()
            if normalized_value in ("true", "1"):
                queryset = queryset.filter(is_active=True)
            elif normalized_value in ("false", "0"):
                queryset = queryset.filter(is_active=False)

        serializer = CatalogItemSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request, catalog_type):
        _validate_catalog_type_or_404(catalog_type)
        _ensure_admin_role(request.user)

        serializer = CatalogItemSerializer(data=request.data, context={"catalog_type": catalog_type})
        serializer.is_valid(raise_exception=True)
        item = serializer.save()
        response_serializer = CatalogItemSerializer(item)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class CatalogItemDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, catalog_type, config_id):
        _validate_catalog_type_or_404(catalog_type)
        return get_object_or_404(CatalogItem, id=config_id, catalog_type=catalog_type)

    def patch(self, request, catalog_type, config_id):
        _ensure_admin_role(request.user)
        item = self.get_object(catalog_type, config_id)
        serializer = CatalogItemSerializer(item, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_item = serializer.save()
        response_serializer = CatalogItemSerializer(updated_item)
        return Response(response_serializer.data)

    def delete(self, request, catalog_type, config_id):
        _ensure_admin_role(request.user)
        item = self.get_object(catalog_type, config_id)
        item.is_active = False
        item.save(update_fields=["is_active", "updated_at"])
        return Response(status=status.HTTP_204_NO_CONTENT)


class CampusListCreateAPIView(MasterDataListCreateBaseAPIView):
    queryset = Campus.objects.select_related().order_by("name")
    serializer_class = CampusSerializer

    def apply_search_filter(self, queryset, search):
        return queryset.filter(Q(code__icontains=search) | Q(name__icontains=search))


class CampusDetailAPIView(MasterDataDetailBaseAPIView):
    queryset = Campus.objects.all()
    serializer_class = CampusSerializer


class AcademicProgramListCreateAPIView(CoordinatorReadableConfigListCreateAPIView):
    queryset = AcademicProgram.objects.select_related("campus").order_by("name")
    serializer_class = AcademicProgramSerializer

    def apply_search_filter(self, queryset, search):
        return queryset.filter(
            Q(code__icontains=search) | Q(name__icontains=search) | Q(campus__name__icontains=search)
        )

    def apply_extra_filters(self, queryset, request):
        campus_id = request.query_params.get("campus_id")
        if campus_id:
            queryset = queryset.filter(campus_id=campus_id)
        return queryset


class AcademicProgramDetailAPIView(MasterDataDetailBaseAPIView):
    queryset = AcademicProgram.objects.all()
    serializer_class = AcademicProgramSerializer


class SubjectListCreateAPIView(CoordinatorReadableConfigListCreateAPIView):
    queryset = Subject.objects.order_by("code")
    serializer_class = SubjectSerializer


class SubjectDetailAPIView(ConfigDetailBaseAPIView):
    queryset = Subject.objects.all()
    serializer_class = SubjectSerializer


class SubjectGroupListCreateAPIView(CoordinatorReadableConfigListCreateAPIView):
    queryset = SubjectGroup.objects.select_related("subject").order_by("subject__code", "identifier")
    serializer_class = SubjectGroupSerializer


class SubjectGroupDetailAPIView(ConfigDetailBaseAPIView):
    queryset = SubjectGroup.objects.select_related("subject").all()
    serializer_class = SubjectGroupSerializer


class SubjectOfferingListCreateAPIView(CoordinatorProtectedAPIView):
    def get(self, _request):
        active_period = get_active_academic_period()
        if active_period is None:
            queryset = SubjectOffering.objects.none()
        else:
            queryset = SubjectOffering.objects.select_related(
                "subject", "academic_program", "academic_period"
            ).filter(academic_period=active_period).order_by("semester", "subject__code")

        serializer = SubjectOfferingSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = SubjectOfferingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        response_serializer = SubjectOfferingSerializer(instance)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class SubjectOfferingDetailAPIView(CoordinatorProtectedAPIView):
    def get_object(self, subject_offering_id):
        return get_object_or_404(
            SubjectOffering.objects.select_related(
                "subject", "subject_group", "working_day", "time_slot",
                "required_space_type", "teacher", "academic_program", "academic_period",
            ),
            id=subject_offering_id,
        )

    def get(self, _request, subject_offering_id):
        instance = self.get_object(subject_offering_id)
        return Response(SubjectOfferingSerializer(instance).data)

    def patch(self, request, subject_offering_id):
        instance = self.get_object(subject_offering_id)
        serializer = SubjectOfferingSerializer(instance, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_instance = serializer.save()
        response_serializer = SubjectOfferingSerializer(updated_instance)
        return Response(response_serializer.data)

    def delete(self, _request, subject_offering_id):
        instance = self.get_object(subject_offering_id)
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MyScheduleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        academic_period_id = request.query_params.get("academic_period_id")
        if not academic_period_id:
            raise ValidationError({"academic_period_id": "Debes seleccionar un periodo academico."})

        academic_period = get_object_or_404(AcademicPeriod, id=academic_period_id)
        if not academic_period.is_schedule_published:
            raise ValidationError({"detail": "El horario de este periodo aun no ha sido publicado."})

        role_name = get_user_role_name(request.user)
        queryset = SubjectOffering.objects.select_related(
            "subject",
            "subject_group",
            "working_day",
            "time_slot",
            "required_space_type",
            "teacher",
            "teacher__user_profile",
            "academic_program",
            "academic_period",
            "assigned_classroom",
            "assigned_classroom__campus",
        ).filter(academic_period=academic_period, is_active=True)

        if role_name == "docente":
            teacher = (
                Teacher.objects.select_related("user_profile")
                .filter(user_profile__user=request.user)
                .first()
                or Teacher.objects.filter(email__iexact=request.user.email).first()
            )
            if teacher is None:
                raise ValidationError({"detail": "No se encontro un docente asociado a su cuenta."})
            queryset = queryset.filter(teacher=teacher)
        elif role_name == "estudiante":
            profile = getattr(request.user, "profile", None)
            if profile is None:
                raise ValidationError({"detail": "No se encontro un perfil de estudiante asociado a su cuenta."})

            queryset = queryset.filter(
                student_enrollments__student=profile,
                student_enrollments__is_active=True,
            )
        elif role_name in {"administrador", "coordinador"} or request.user.is_superuser:
            queryset = queryset
        else:
            raise ValidationError({"detail": "Rol no habilitado para consultar horarios."})

        serializer = MyScheduleSerializer(queryset.distinct(), many=True)
        return Response(serializer.data)


class StudentEnrollmentListCreateAPIView(AdminProtectedAPIView):
    def get_queryset(self):
        return StudentEnrollment.objects.select_related(
            "student",
            "student__role",
            "student__user",
            "subject_offering",
            "subject_offering__subject",
            "subject_offering__subject_group",
            "subject_offering__working_day",
            "subject_offering__time_slot",
            "subject_offering__academic_program",
            "subject_offering__academic_period",
            "subject_offering__teacher",
        ).order_by("student__last_name", "student__first_name", "subject_offering_id")

    def get(self, _request):
        serializer = StudentEnrollmentSerializer(self.get_queryset(), many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = StudentEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(StudentEnrollmentSerializer(instance).data, status=status.HTTP_201_CREATED)


class TeacherListCreateAPIView(CoordinatorProtectedAPIView):
    def _get_queryset(self, request):
        queryset = Teacher.objects.select_related("link_type").order_by("last_name", "first_name")
        queryset = _filter_by_is_active_param(queryset, request)

        search = request.query_params.get("search")
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
                | Q(email__icontains=search)
            )

        link_type_id = request.query_params.get("link_type_id")
        if link_type_id:
            queryset = queryset.filter(link_type_id=link_type_id)

        return queryset

    def get(self, request):
        serializer = TeacherSerializer(self._get_queryset(request), many=True)
        return Response(serializer.data)

    def post(self, request):
        if get_user_role_name(request.user) != "administrador":
            raise PermissionDenied("Solo administradores pueden crear docentes.")
        serializer = TeacherSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        return Response(TeacherSerializer(instance).data, status=status.HTTP_201_CREATED)


class TeacherDetailAPIView(MasterDataDetailBaseAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer


class CourseListCreateAPIView(MasterDataListCreateBaseAPIView):
    queryset = Course.objects.select_related("academic_program", "class_type").order_by("code")
    serializer_class = CourseSerializer

    def apply_search_filter(self, queryset, search):
        return queryset.filter(Q(code__icontains=search) | Q(name__icontains=search))

    def apply_extra_filters(self, queryset, request):
        academic_program_id = request.query_params.get("academic_program_id")
        class_type_id = request.query_params.get("class_type_id")

        if academic_program_id:
            queryset = queryset.filter(academic_program_id=academic_program_id)
        if class_type_id:
            queryset = queryset.filter(class_type_id=class_type_id)

        return queryset


class CourseDetailAPIView(MasterDataDetailBaseAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer


class CourseGroupListCreateAPIView(MasterDataListCreateBaseAPIView):
    queryset = CourseGroup.objects.select_related("course").order_by("course_id", "identifier")
    serializer_class = CourseGroupSerializer

    def apply_search_filter(self, queryset, search):
        return queryset.filter(
            Q(identifier__icontains=search)
            | Q(course__code__icontains=search)
            | Q(course__name__icontains=search)
        )

    def apply_extra_filters(self, queryset, request):
        course_id = request.query_params.get("course_id")
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        return queryset


class CourseGroupDetailAPIView(MasterDataDetailBaseAPIView):
    queryset = CourseGroup.objects.all()
    serializer_class = CourseGroupSerializer


class ClassroomListCreateAPIView(MasterDataListCreateBaseAPIView):
    queryset = Classroom.objects.select_related("campus", "space_type").order_by("code")
    serializer_class = ClassroomSerializer

    def apply_search_filter(self, queryset, search):
        return queryset.filter(Q(code__icontains=search) | Q(name__icontains=search))

    def apply_extra_filters(self, queryset, request):
        campus_id = request.query_params.get("campus_id")
        space_type_id = request.query_params.get("space_type_id")
        is_accessible = request.query_params.get("is_accessible")

        if campus_id:
            queryset = queryset.filter(campus_id=campus_id)
        if space_type_id:
            queryset = queryset.filter(space_type_id=space_type_id)
        if is_accessible is not None:
            normalized = is_accessible.strip().lower()
            if normalized in ("true", "1"):
                queryset = queryset.filter(is_accessible=True)
            elif normalized in ("false", "0"):
                queryset = queryset.filter(is_accessible=False)

        return queryset


class ClassroomDetailAPIView(MasterDataDetailBaseAPIView):
    queryset = Classroom.objects.all()
    serializer_class = ClassroomSerializer


class MasterDataImportAPIView(APIView):
    permission_classes = [IsAuthenticated, HasAllowedRoles]
    allowed_roles = ("administrador",)
    parser_classes = [MultiPartParser, FormParser]

    def get(self, _request):
        return Response({"templates": get_import_templates()})

    def post(self, request):
        resource_type = request.data.get("resource_type")
        source_file = request.FILES.get("file")

        if not resource_type:
            raise ValidationError({"resource_type": "El tipo de recurso es obligatorio."})
        if not source_file:
            raise ValidationError({"file": "Debes adjuntar un archivo CSV o XLSX."})

        try:
            result = import_master_data(file_obj=source_file, resource_type=resource_type)
        except MasterDataImportError as exc:
            raise ValidationError({"file": str(exc)}) from exc

        return Response(result, status=status.HTTP_200_OK)


class HorarioAPIView(AdminProtectedAPIView):
    def get(self, request):
        queryset = (
            SubjectOffering.objects.select_related(
                "working_day",
                "time_slot",
                "subject",
                "teacher",
                "subject_group",
                "assigned_classroom",
                "assigned_classroom__campus",
                "academic_period",
                "academic_program__campus",
            )
            .filter(working_day__isnull=False, time_slot__isnull=False)
            .order_by("working_day__day_of_week", "time_slot__start_time")
        )

        period_id = request.query_params.get("period_id")
        campus_id = request.query_params.get("campus_id")
        program_id = request.query_params.get("program_id")
        semester = request.query_params.get("semester")

        if period_id:
            queryset = queryset.filter(academic_period_id=period_id)
        if campus_id:
            queryset = queryset.filter(academic_program__campus_id=campus_id)
        if program_id:
            queryset = queryset.filter(academic_program_id=program_id)
        if semester:
            queryset = queryset.filter(semester=semester)

        serializer = HorarioOfferingSerializer(queryset, many=True)
        return Response({"assignments": serializer.data})


class HorarioNoAsignadasAPIView(AdminProtectedAPIView):
    def get(self, request):
        queryset = (
            SubjectOffering.objects.select_related("subject", "subject_group", "academic_period")
            .filter(working_day__isnull=True)
            .order_by("subject__name")
        )

        period_id = request.query_params.get("period_id")
        campus_id = request.query_params.get("campus_id")
        program_id = request.query_params.get("program_id")
        semester = request.query_params.get("semester")

        if period_id:
            queryset = queryset.filter(academic_period_id=period_id)
        if campus_id:
            queryset = queryset.filter(academic_program__campus_id=campus_id)
        if program_id:
            queryset = queryset.filter(academic_program_id=program_id)
        if semester:
            queryset = queryset.filter(semester=semester)

        serializer = HorarioUnassignedSerializer(queryset, many=True)
        return Response({"unassigned": serializer.data})


class ScheduleExecutionListCreateAPIView(AdminProtectedAPIView):
    def get(self, request):
        queryset = ScheduleExecution.objects.select_related("academic_period", "requested_by")
        period_id = request.query_params.get("period_id")
        status_value = request.query_params.get("status")

        if period_id:
            queryset = queryset.filter(academic_period_id=period_id)
        if status_value:
            queryset = queryset.filter(status=status_value)

        serializer = ScheduleExecutionSerializer(queryset, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = ScheduleExecutionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        validated_data = serializer.validated_data
        academic_period = validated_data["academic_period"]

        if not academic_period.is_active:
            raise ValidationError({"academic_period_id": "El periodo academico debe estar activo."})

        execution = ScheduleExecution.objects.create(
            academic_period=academic_period,
            requested_by=request.user,
            status=ScheduleExecution.Status.PENDING,
            progress=0,
            parameters={
                "poblacion_size": validated_data["poblacion_size"],
                "generaciones": validated_data["generaciones"],
                "proporcion_heuristica": validated_data["proporcion_heuristica"],
                "estancamiento_max": validated_data["estancamiento_max"],
            },
        )

        transaction.on_commit(lambda: queue_schedule_execution(execution.id))

        response_serializer = ScheduleExecutionSerializer(execution)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)


class ScheduleExecutionDetailAPIView(AdminProtectedAPIView):
    def get_object(self, execution_id):
        return get_object_or_404(
            ScheduleExecution.objects.select_related("academic_period", "requested_by"),
            id=execution_id,
        )

    def get(self, _request, execution_id):
        execution = self.get_object(execution_id)
        return Response(ScheduleExecutionSerializer(execution).data)


class ScheduleValidationAPIView(AdminProtectedAPIView):
    def get(self, request):
        period_id = request.query_params.get("period_id")
        if not period_id:
            raise ValidationError({"period_id": "Debes seleccionar un periodo academico."})

        academic_period = get_object_or_404(AcademicPeriod, id=period_id)
        return Response(validate_schedule_before_execution(academic_period))
