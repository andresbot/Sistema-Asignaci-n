from django.db.models import Q
from django.shortcuts import get_object_or_404
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
    SpaceType,
    Subject,
    SubjectGroup,
    SubjectOffering,
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
    LoginSerializer,
    RoleSerializer,
    SpaceTypeSerializer,
    SubjectGroupSerializer,
    SubjectOfferingSerializer,
    SubjectSerializer,
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
