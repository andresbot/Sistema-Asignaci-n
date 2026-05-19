from django.contrib import admin

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


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "email", "first_name", "last_name", "role", "is_active")
    search_fields = ("user__username", "email", "first_name", "last_name")
    list_filter = ("role", "is_active")


@admin.register(AcademicPeriod)
class AcademicPeriodAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "start_date", "end_date", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(AcademicProgram)
class AcademicProgramAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "campus", "is_active")
    search_fields = ("code", "name", "campus__name")
    list_filter = ("campus", "is_active")


@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = (
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
    )
    search_fields = ("code", "name")
    list_filter = ("is_active", "class_type")


@admin.register(SubjectGroup)
class SubjectGroupAdmin(admin.ModelAdmin):
    list_display = ("subject", "identifier", "is_active", "created_at", "updated_at")
    search_fields = ("subject__code", "identifier")
    list_filter = ("is_active", "subject")


@admin.register(SubjectOffering)
class SubjectOfferingAdmin(admin.ModelAdmin):
    list_display = (
        "subject",
        "subject_group",
        "working_day",
        "time_slot",
        "academic_program",
        "academic_period",
        "semester",
        "is_active",
    )
    search_fields = (
        "subject__code",
        "subject_group__identifier",
        "working_day__name",
        "time_slot__name",
        "academic_program__code",
        "academic_period__code",
    )
    list_filter = ("is_active", "working_day", "time_slot", "academic_period", "academic_program")


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ("name", "start_time", "end_time", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(WorkingDay)
class WorkingDayAdmin(admin.ModelAdmin):
    list_display = ("day_of_week", "name", "is_active")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(SpaceType)
class SpaceTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at", "updated_at")
    search_fields = ("name",)
    list_filter = ("is_active",)


@admin.register(CatalogItem)
class CatalogItemAdmin(admin.ModelAdmin):
    list_display = ("catalog_type", "name", "is_active", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("catalog_type", "is_active")


@admin.register(Campus)
class CampusAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "is_active")
    search_fields = ("code", "name")
    list_filter = ("is_active",)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "email", "link_type", "hourly_rate", "is_active")
    search_fields = ("first_name", "last_name", "email")
    list_filter = ("link_type", "is_active")


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "academic_program", "class_type", "credits", "weekly_hours", "is_active")
    search_fields = ("code", "name", "academic_program__name")
    list_filter = ("academic_program", "class_type", "is_active")


@admin.register(CourseGroup)
class CourseGroupAdmin(admin.ModelAdmin):
    list_display = ("course", "identifier", "student_count", "is_active")
    search_fields = ("identifier", "course__code", "course__name")
    list_filter = ("course", "is_active")


@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "campus", "space_type", "capacity", "is_accessible", "is_active")
    search_fields = ("code", "name", "campus__name")
    list_filter = ("campus", "space_type", "is_accessible", "is_active")
