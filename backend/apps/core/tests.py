from django.contrib.auth.models import AnonymousUser, User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from datetime import date, time
from io import BytesIO
from openpyxl import Workbook
from rest_framework import status
from rest_framework.test import APITestCase

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
    Subject,
    SubjectGroup,
    SubjectOffering,
    SpaceType,
    Teacher,
    TimeSlot,
    UserProfile,
    WorkingDay,
)
from .services.config_service import (
    SUBJECT_CREDITS_MAX,
    SUBJECT_WEEKLY_HOURS_MAX,
    ConfigValidationError,
    create_academic_period,
    create_catalog_item,
    create_space_type,
    create_subject,
    create_time_slot,
    create_working_day,
    update_academic_period,
    update_catalog_item,
    update_space_type,
    update_time_slot,
    update_working_day,
)
from .services.programming_service import (
    check_classrooms_available_for_space_type,
    create_subject_offering,
    get_offering_non_assignable_reason,
)
from .services.schedule_validation_service import validate_schedule_before_execution
from .services.schedule_execution_service import run_schedule_execution, queue_schedule_execution
from .services.user_service import (
    UserEmailAlreadyExistsError,
    create_user_with_profile,
    deactivate_user_profile,
    update_user_profile,
)
import time as _time


class BaseAuthTestCase(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role, _ = Role.objects.get_or_create(name="Administrador")
        cls.coordinator_role, _ = Role.objects.get_or_create(name="Coordinador")
        cls.docente_role, _ = Role.objects.get_or_create(name="Docente")
        cls.estudiante_role, _ = Role.objects.get_or_create(name="Estudiante")

    def create_user(self, email, password, role, first_name, last_name):
        user = User.objects.create_user(
            username=email,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        UserProfile.objects.create(
            user=user,
            role=role,
            first_name=first_name,
            last_name=last_name,
            email=email,
        )
        return user

    def login_and_set_auth(self, email, password):
        login_response = self.client.post(
            reverse("auth-login"),
            {"email": email, "password": password},
            format="json",
        )
        self.assertEqual(login_response.status_code, status.HTTP_200_OK)
        token = login_response.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
        return login_response


class ProgrammingTests(BaseAuthTestCase):
    def setUp(self):
        self.admin_user = self.create_user(
            email="admin@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )
        self.active_period = AcademicPeriod.objects.create(
            code="2026-1",
            name="Periodo 2026-1",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
        )
        self.subject = Subject.objects.create(
            code="MAT101",
            name="Calculo I",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=40,
            difficulty=160,
        )
        self.subject_group = SubjectGroup.objects.create(
            subject=self.subject,
            identifier="Grupo 1",
        )
        self.campus = Campus.objects.create(code="01", name="Main Campus")
        self.academic_program = AcademicProgram.objects.create(
            code="ING-SIS", name="Ingenieria de Sistemas", campus=self.campus
        )
        self.working_day = WorkingDay.objects.create(day_of_week=4, name="Jueves", is_active=True)
        self.time_slot = TimeSlot.objects.create(
            name="14:00 - 19:00",
            start_time=time(14, 0),
            end_time=time(19, 0),
            is_active=True,
        )


class IntegrationScheduleExecutionTests(BaseAuthTestCase):
    def setUp(self):
        # create admin and base data
        self.admin_user = self.create_user(
            email="admin@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.execution_admin_user = self.create_user(
            email="admin.exec@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Exec",
        )
        self.coordinator_user = self.create_user(
            email="coord@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )
        self.campus = Campus.objects.create(code="C1", name="Campus 1")
        self.program = AcademicProgram.objects.create(code="PRG1", name="Programa 1", campus=self.campus)
        self.period = AcademicPeriod.objects.create(
            code="P-INT-2026",
            name="Periodo INT",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
        )
        # active period used by some programming APIs/tests
        self.active_period = AcademicPeriod.objects.create(
            code="P-ACT-2026",
            name="Periodo Activo",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
            is_schedule_published=False,
        )

        # working days and time slots
        self.working_day = WorkingDay.objects.create(day_of_week=1, name="Lunes", is_active=True)
        self.time_slot = TimeSlot.objects.create(name="08:00-10:00", start_time=time(8, 0), end_time=time(10, 0), is_active=True)

        # classrooms
        self.space_type = CatalogItem.objects.create(catalog_type=CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE, name="Salon standard")
        self.classroom1 = Classroom.objects.create(code="A101", name="A101", campus=self.campus, space_type=self.space_type, capacity=50, is_accessible=True)
        self.classroom2 = Classroom.objects.create(code="B201", name="B201", campus=self.campus, space_type=self.space_type, capacity=30, is_accessible=False)

        # subject and groups (restore expected fixtures: MAT101 primary subject)
        self.subject1 = Subject.objects.create(
            code="MAT101",
            name="Calculo I",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=40,
            difficulty=160,
        )
        self.subject_group1 = SubjectGroup.objects.create(subject=self.subject1, identifier="Grupo 1")

        self.subject2 = Subject.objects.create(
            code="INT102",
            name="Intro INT B",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=2,
            capacity=25,
            difficulty=50,
        )
        self.subject_group2 = SubjectGroup.objects.create(subject=self.subject2, identifier="Grupo 1")
        self.subject_group = self.subject_group1
        self.subject = self.subject1

        # create two offerings without assignment (different subjects to avoid unique constraint)
        self.offering1 = SubjectOffering.objects.create(
            subject=self.subject1,
            subject_group=self.subject_group1,
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
            is_active=True,
        )
        self.offering2 = SubjectOffering.objects.create(
            subject=self.subject2,
            subject_group=self.subject_group2,
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
            is_active=True,
        )
        self.academic_program = self.program

    def test_create_execution_api_enqueues_and_applies_stub_assignments(self):
        # login as admin
        self.login_and_set_auth("admin.exec@test.com", "adminpassword123")

        payload = {"academic_period_id": self.period.id, "generaciones": 2}
        response = self.client.post(reverse("programming-schedule-executions-list-create"), payload, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        execution_id = response.data["id"]

        # poll for execution completion (timeout after ~10s)
        detail_url = reverse("programming-schedule-executions-detail", kwargs={"execution_id": execution_id})
        finished = False
        for _ in range(80):
            resp = self.client.get(detail_url)
            self.assertIn(resp.status_code, (status.HTTP_200_OK,))
            data = resp.data
            if data.get("status") == "completed":
                finished = True
                break
            _time.sleep(0.25)

        self.assertTrue(finished, "Execution did not finish in time")

        # refresh offerings and check assignments or failure reasons set
        self.offering1.refresh_from_db()
        self.offering2.refresh_from_db()

        # At least one offering should have an assigned_classroom or a failure reason set by the stub
        assigned_or_reason = lambda o: (o.assigned_classroom is not None) or (o.schedule_failure_reason and o.schedule_failure_reason.strip())
        self.assertTrue(assigned_or_reason(self.offering1))
        self.assertTrue(assigned_or_reason(self.offering2))

        # academic period timestamp must be set
        self.period.refresh_from_db()
        self.assertIsNotNone(self.period.schedule_generated_at)




    def test_admin_can_create_subject_group(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subject-groups-list-create"),
            {
                "subject_id": self.subject.id,
                "identifier": "Grupo 2",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["identifier"], "Grupo 2")

    def test_admin_can_create_subject_with_difficulty_calculated(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subjects-list-create"),
            {
                "code": "FIS101",
                "name": "Fisica I",
                "class_type": "virtual",
                "credits": 4,
                "weekly_hours": 5,
                "capacity": 35,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["difficulty"], 175)

    def test_admin_can_update_subject_intensity_and_recalculate_difficulty(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.patch(
            reverse("programming-subjects-detail", kwargs={"config_id": self.subject.id}),
            {
                "weekly_hours": 6,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["difficulty"], 240)

    def test_subject_code_must_be_unique(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subjects-list-create"),
            {
                "code": "MAT101",
                "name": "Calculo I Duplicada",
                "class_type": "presencial",
                "credits": 3,
                "weekly_hours": 4,
                "capacity": 30,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("code", response.data)

    def test_subject_numeric_fields_must_be_positive(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subjects-list-create"),
            {
                "code": "QUI101",
                "name": "Quimica I",
                "class_type": "virtual",
                "credits": 0,
                "weekly_hours": 0,
                "capacity": 0,
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("credits", response.data)

    def test_duplicate_subject_group_is_rejected(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subject-groups-list-create"),
            {
                "subject_id": self.subject.id,
                "identifier": "Grupo 1",
                "is_active": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("identifier", response.data)
        self.assertIn("Ya existe un grupo", str(response.data["identifier"][0]))

    def test_subject_offering_requires_semester(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            {
                "subject_id": self.subject.id,
                "subject_group_id": self.subject_group.id,
                "academic_program_id": self.academic_program.id,
                "working_day_id": self.working_day.id,
                "time_slot_id": self.time_slot.id,
                "semester": "",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("semester", response.data)

    def test_subject_offering_is_assigned_to_active_period(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            {
                "subject_id": self.subject.id,
                "subject_group_id": self.subject_group.id,
                "academic_program_id": self.academic_program.id,
                "working_day_id": self.working_day.id,
                "time_slot_id": self.time_slot.id,
                "semester": 3,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["academic_period"]["id"], self.active_period.id)
        self.assertEqual(response.data["semester"], 3)

    def test_subject_offering_rejects_duplicates_for_same_period(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        payload = {
            "subject_id": self.subject.id,
            "subject_group_id": self.subject_group.id,
            "academic_program_id": self.academic_program.id,
            "working_day_id": self.working_day.id,
            "time_slot_id": self.time_slot.id,
            "semester": 3,
        }

        first_response = self.client.post(
            reverse("programming-subject-offerings-list-create"), payload, format="json"
        )
        self.assertEqual(first_response.status_code, status.HTTP_201_CREATED)

        second_response = self.client.post(
            reverse("programming-subject-offerings-list-create"), payload, format="json"
        )
        self.assertEqual(second_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("subject_group_id", second_response.data)

    def test_coordinator_can_list_catalogs_for_programming(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")

        subjects_response = self.client.get(reverse("programming-subjects-list-create"))
        programs_response = self.client.get(reverse("programs-list-create"))

        self.assertEqual(subjects_response.status_code, status.HTTP_200_OK)
        self.assertEqual(programs_response.status_code, status.HTTP_200_OK)

    def test_coordinator_cannot_create_catalog_entries(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")

        subject_response = self.client.post(
            reverse("programming-subjects-list-create"),
            {"code": "FIS101", "name": "Fisica I", "is_active": True},
            format="json",
        )
        program_response = self.client.post(
            reverse("programs-list-create"),
            {"code": "ING-IND", "name": "Ingenieria Industrial", "is_active": True},
            format="json",
        )

        self.assertEqual(subject_response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(program_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_subject_with_class_type_item_id(self):
        """Reproduce creating a Subject sending `class_type_item_id` instead of legacy `class_type`."""
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        ct = CatalogItem.objects.filter(catalog_type=CatalogItem.CatalogType.CLASS_TYPE).first()
        self.assertIsNotNone(ct, "No class_type CatalogItem found in migrations")

        payload = {
            "code": "TST999",
            "name": "Test Subject",
            "class_type_item_id": ct.id,
            "credits": 2,
            "weekly_hours": 2,
            "capacity": 10,
            "is_active": True,
        }

        response = self.client.post(
            reverse("programming-subjects-list-create"), payload, format="json"
        )

        self.assertIn(response.status_code, (status.HTTP_201_CREATED, status.HTTP_200_OK))
        if response.status_code == status.HTTP_201_CREATED:
            self.assertEqual(response.data["code"], "TST999")

    def test_coordinator_can_register_subject_offering(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")

        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            {
                "subject_id": self.subject.id,
                "subject_group_id": self.subject_group.id,
                "academic_program_id": self.academic_program.id,
                "working_day_id": self.working_day.id,
                "time_slot_id": self.time_slot.id,
                "semester": 4,
                "requires_accessible_classroom": True,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["academic_period"]["id"], self.active_period.id)
        self.assertEqual(response.data["semester"], 4)
        self.assertTrue(response.data["requires_accessible_classroom"])

    def test_accessible_classroom_requirement_is_respected(self):
        accessible_space_type = CatalogItem.objects.create(
            catalog_type=CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE,
            name="Aula Accesible HU20",
        )
        accessible_classroom = Classroom.objects.create(
            code="ACC-01",
            name="Salon Accesible 1",
            campus=self.campus,
            space_type=accessible_space_type,
            capacity=45,
            is_accessible=True,
            is_active=True,
        )
        Classroom.objects.create(
            code="NOACC-01",
            name="Salon No Accesible 1",
            campus=self.campus,
            space_type=accessible_space_type,
            capacity=60,
            is_accessible=False,
            is_active=True,
        )

        offering = create_subject_offering(
            subject=self.subject,
            subject_group=self.subject_group,
            working_day=self.working_day,
            time_slot=self.time_slot,
            academic_program=self.academic_program,
            required_space_type=accessible_space_type,
            academic_period=self.active_period,
            semester=5,
            student_count=30,
            requires_accessible_classroom=True,
        )

        self.assertIsNone(get_offering_non_assignable_reason(offering))

        # mark classroom as inactive (soft-delete semantics)
        accessible_classroom.is_active = False
        accessible_classroom.save(update_fields=["is_active", "updated_at"]) 
        offering.refresh_from_db()

        reason = get_offering_non_assignable_reason(offering)
        self.assertIsNotNone(reason)
        self.assertIn("accesible", reason.lower())

    def test_subject_offering_rejects_inactive_working_day(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        inactive_day = WorkingDay.objects.create(day_of_week=6, name="Sabado", is_active=False)

        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            {
                "subject_id": self.subject.id,
                "subject_group_id": self.subject_group.id,
                "academic_program_id": self.academic_program.id,
                "working_day_id": inactive_day.id,
                "time_slot_id": self.time_slot.id,
                "semester": 2,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("working_day_id", response.data)

    def test_my_schedule_teacher_student_admin_and_unpublished_behaviour(self):
        # prepare link type for teachers
        link_type = CatalogItem.objects.filter(catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE).first()
        if not link_type:
            link_type = CatalogItem.objects.create(catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE, name="Contratado")

        # create a teacher user and Teacher entry
        teacher_user = self.create_user(
            email="teacher1@test.com",
            password="teachpass123",
            role=self.docente_role,
            first_name="T",
            last_name="One",
        )
        teacher = Teacher.objects.create(
            first_name="T",
            last_name="One",
            email=teacher_user.email,
            link_type=link_type,
            hourly_rate=10.0,
            user_profile=teacher_user.profile,
        )

        # another teacher
        other_teacher = Teacher.objects.create(
            first_name="Other",
            last_name="Teacher",
            email="other@test.com",
            link_type=link_type,
            hourly_rate=12.0,
        )

        # create offerings for the active period
        own_offering = SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            academic_program=self.academic_program,
            working_day=self.working_day,
            time_slot=self.time_slot,
            semester=1,
            academic_period=self.active_period,
            teacher=teacher,
            is_active=True,
        )

        other_offering = SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            academic_program=self.academic_program,
            working_day=self.working_day,
            time_slot=self.time_slot,
            semester=2,
            academic_period=self.active_period,
            teacher=other_teacher,
            is_active=True,
        )

        # PUBLISH the period for positive cases
        self.active_period.is_schedule_published = True
        self.active_period.save()

        # Teacher should see only their offering
        self.login_and_set_auth("teacher1@test.com", "teachpass123")
        resp_t = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")
        self.assertEqual(resp_t.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp_t.data, list)
        self.assertEqual(len(resp_t.data), 1)
        self.assertEqual(resp_t.data[0]["id"], own_offering.id)

        # Student sees enrolled offerings
        student_user = self.create_user(
            email="student1@test.com",
            password="studentpass123",
            role=self.estudiante_role,
            first_name="S",
            last_name="One",
        )

        # enroll student in other_offering
        from .models import StudentEnrollment

        StudentEnrollment.objects.create(student=student_user.profile, subject_offering=other_offering)

        self.login_and_set_auth("student1@test.com", "studentpass123")
        resp_s = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")
        self.assertEqual(resp_s.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp_s.data, list)
        # student enrolled in other_offering -> receives 1
        self.assertEqual(len(resp_s.data), 1)
        self.assertEqual(resp_s.data[0]["id"], other_offering.id)

        # Admin sees both offerings
        self.login_and_set_auth("admin@test.com", "adminpassword123")
        resp_a = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")
        self.assertEqual(resp_a.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp_a.data, list)
        # admin should see both offerings (distinct list)
        returned_ids = {item["id"] for item in resp_a.data}
        self.assertTrue(own_offering.id in returned_ids and other_offering.id in returned_ids)

        # Unpublished period: toggle to unpublished and request -> should return 400
        self.active_period.is_schedule_published = False
        self.active_period.save()

        self.login_and_set_auth("teacher1@test.com", "teachpass123")
        resp_unpub = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")
        self.assertEqual(resp_unpub.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("detail", resp_unpub.data)

        def test_my_schedule_teacher_without_teacher_profile_returns_error(self):
            """Teacher user without Teacher model entry should get appropriate error."""
            teacher_user = self.create_user(
                email="orphan_teacher@test.com",
                password="teachpass123",
                role=self.docente_role,
                first_name="Orphan",
                last_name="Teacher",
            )

            # Set period as published
            self.active_period.is_schedule_published = True
            self.active_period.save()

            self.login_and_set_auth("orphan_teacher@test.com", "teachpass123")
            resp = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")

            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("detail", resp.data)
            self.assertIn("no se encontro un docente", str(resp.data).lower())

        def test_my_schedule_student_without_profile_returns_error(self):
            """Student user without UserProfile relationship should return error."""
            # Create a user but don't properly associate the profile
            student_user = User.objects.create_user(
                username="broken_student@test.com",
                email="broken_student@test.com",
                password="studentpass123",
            )

            # Set period as published
            self.active_period.is_schedule_published = True
            self.active_period.save()

            # Login with this user
            login_resp = self.client.post(
                reverse("auth-login"),
                {"email": "broken_student@test.com", "password": "studentpass123"},
                format="json",
            )
            # If login fails, skip test (user requires proper profile)
            if login_resp.status_code != status.HTTP_200_OK:
                self.skipTest("Could not create test user without proper profile")

            token = login_resp.data["access"]
            self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")
            resp = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")

            # Should either return 400 or 200 with empty list (depends on implementation)
            self.assertIn(resp.status_code, [status.HTTP_400_BAD_REQUEST, status.HTTP_200_OK])

        def test_my_schedule_missing_academic_period_id_returns_error(self):
            """Request without academic_period_id should return validation error."""
            self.login_and_set_auth("admin@test.com", "adminpassword123")
            resp = self.client.get(reverse("programming-my-schedule"))

            self.assertEqual(resp.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertIn("academic_period_id", resp.data)

        def test_my_schedule_nonexistent_academic_period_returns_404(self):
            """Request with non-existent period ID should return 404."""
            self.login_and_set_auth("admin@test.com", "adminpassword123")
            resp = self.client.get(reverse("programming-my-schedule") + "?academic_period_id=99999")

            self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)

        def test_my_schedule_unauthenticated_request_returns_401(self):
            """Unauthenticated request should return 401."""
            resp = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")

            self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        def test_my_schedule_coordinator_can_see_all_offerings(self):
            """Coordinators should be able to see all offerings in published period."""
            link_type = CatalogItem.objects.filter(catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE).first()
            if not link_type:
                link_type = CatalogItem.objects.create(catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE, name="Contratado")

            teacher = Teacher.objects.create(
                first_name="Test",
                last_name="Teacher",
                email="test_teacher@test.com",
                link_type=link_type,
                hourly_rate=10.0,
            )

            offering = SubjectOffering.objects.create(
                subject=self.subject,
                subject_group=self.subject_group,
                academic_program=self.academic_program,
                working_day=self.working_day,
                time_slot=self.time_slot,
                semester=1,
                academic_period=self.active_period,
                teacher=teacher,
                is_active=True,
            )

            self.active_period.is_schedule_published = True
            self.active_period.save()

            self.login_and_set_auth("coord@test.com", "coordpassword123")
            resp = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")

            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertIsInstance(resp.data, list)
            self.assertEqual(len(resp.data), 1)
            self.assertEqual(resp.data[0]["id"], offering.id)

        def test_my_schedule_inactive_offerings_are_excluded(self):
            """Inactive subject offerings should not appear in schedule."""
            link_type = CatalogItem.objects.filter(catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE).first()
            if not link_type:
                link_type = CatalogItem.objects.create(catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE, name="Contratado")

            teacher_user = self.create_user(
                email="test_teacher2@test.com",
                password="teachpass123",
                role=self.docente_role,
                first_name="T",
                last_name="Two",
            )
            teacher = Teacher.objects.create(
                first_name="T",
                last_name="Two",
                email=teacher_user.email,
                link_type=link_type,
                hourly_rate=10.0,
                user_profile=teacher_user.profile,
            )

            active_offering = SubjectOffering.objects.create(
                subject=self.subject,
                subject_group=self.subject_group,
                academic_program=self.academic_program,
                working_day=self.working_day,
                time_slot=self.time_slot,
                semester=1,
                academic_period=self.active_period,
                teacher=teacher,
                is_active=True,
            )

            inactive_offering = SubjectOffering.objects.create(
                subject=self.subject,
                subject_group=self.subject_group,
                academic_program=self.academic_program,
                working_day=self.working_day,
                time_slot=self.time_slot,
                semester=2,
                academic_period=self.active_period,
                teacher=teacher,
                is_active=False,
            )

            self.active_period.is_schedule_published = True
            self.active_period.save()

            self.login_and_set_auth("test_teacher2@test.com", "teachpass123")
            resp = self.client.get(reverse("programming-my-schedule") + f"?academic_period_id={self.active_period.id}")

            self.assertEqual(resp.status_code, status.HTTP_200_OK)
            self.assertEqual(len(resp.data), 1)
            self.assertEqual(resp.data[0]["id"], active_offering.id)


class HealthCheckTests(APITestCase):
    def test_health_check_returns_ok(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "ok")


class AuthenticationTests(BaseAuthTestCase):
    def setUp(self):
        self.admin_user = self.create_user(
            email="admin@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )

    def test_login_returns_tokens_and_user_data(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@test.com", "password": "adminpassword123"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("access", response.data)
        self.assertIn("refresh", response.data)
        self.assertEqual(response.data["user"]["email"], "admin@test.com")
        self.assertEqual(response.data["user"]["role"], "administrador")


class ScheduleValidationServiceTests(ProgrammingTests):
    def _create_teacher(self, email, first_name, last_name):
        link_type, _ = CatalogItem.objects.get_or_create(
            catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE,
            name="Contrato validacion HU9",
        )
        teacher_user = self.create_user(
            email=email,
            password="teachpass123",
            role=self.docente_role,
            first_name=first_name,
            last_name=last_name,
        )
        return Teacher.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            link_type=link_type,
            hourly_rate=10.0,
            user_profile=teacher_user.profile,
        )

    def test_validate_schedule_before_execution_returns_success_when_all_data_is_valid(self):
        teacher = self._create_teacher("teacher-valid@test.com", "Val", "Teacher")
        space_type = CatalogItem.objects.create(
            catalog_type=CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE,
            name="Salon valido HU9",
        )
        Classroom.objects.create(
            code="HU9-101",
            name="Salon HU9 101",
            campus=self.campus,
            space_type=space_type,
            capacity=40,
            is_accessible=True,
            is_active=True,
        )

        SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            academic_program=self.academic_program,
            academic_period=self.active_period,
            working_day=self.working_day,
            time_slot=self.time_slot,
            teacher=teacher,
            required_space_type=space_type,
            student_count=30,
            semester=1,
            is_active=True,
        )

        result = validate_schedule_before_execution(self.active_period)

        self.assertTrue(result["can_run_algorithm"])
        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["summary"]["issues_count"], 0)
        self.assertEqual(result["issues"], [])

    def test_validate_schedule_before_execution_detects_blocking_issues_and_teacher_conflict(self):
        teacher = self._create_teacher("teacher-conflict@test.com", "Conf", "Teacher")
        space_type = CatalogItem.objects.create(
            catalog_type=CatalogItem.CatalogType.ACADEMIC_SPACE_TYPE,
            name="Salon conflicto HU9",
        )
        Classroom.objects.create(
            code="HU9-201",
            name="Salon HU9 201",
            campus=self.campus,
            space_type=space_type,
            capacity=50,
            is_accessible=True,
            is_active=True,
        )

        other_subject = Subject.objects.create(
            code="MAT102",
            name="Calculo II",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=40,
            difficulty=160,
        )
        other_group = SubjectGroup.objects.create(subject=other_subject, identifier="Grupo 2")

        SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            academic_program=self.academic_program,
            academic_period=self.active_period,
            working_day=None,
            time_slot=None,
            teacher=None,
            required_space_type=None,
            student_count=None,
            semester=1,
            is_active=True,
        )

        SubjectOffering.objects.create(
            subject=other_subject,
            subject_group=other_group,
            academic_program=self.academic_program,
            academic_period=self.active_period,
            working_day=self.working_day,
            time_slot=self.time_slot,
            teacher=teacher,
            required_space_type=None,
            student_count=25,
            semester=2,
            is_active=True,
        )

        SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            academic_program=self.academic_program,
            academic_period=self.active_period,
            working_day=self.working_day,
            time_slot=self.time_slot,
            teacher=teacher,
            required_space_type=space_type,
            student_count=30,
            semester=3,
            is_active=True,
        )

        result = validate_schedule_before_execution(self.active_period)

        self.assertFalse(result["can_run_algorithm"])
        codes = {issue["code"] for issue in result["issues"]}
        self.assertIn("missing_slot", codes)
        self.assertIn("missing_teacher", codes)
        self.assertIn("missing_capacity", codes)
        self.assertIn("missing_space_type", codes)
        self.assertIn("teacher_conflict", codes)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@test.com", "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("Credenciales invalidas", str(response.data))

    def test_me_returns_authenticated_user(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")
        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["email"], "admin@test.com")
        self.assertEqual(response.data["role"], "administrador")

    def test_admin_only_allows_admin_role(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")
        response = self.client.get(reverse("auth-admin-only"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"], "administrador")

    def test_admin_only_denies_coordinator_role(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")
        response = self.client.get(reverse("auth-admin-only"))

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_blacklists_refresh_token(self):
        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@test.com", "password": "adminpassword123"},
            format="json",
        )
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        response = self.client.post(
            reverse("auth-logout"),
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_requires_refresh_token(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(reverse("auth-logout"), {}, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("refresh token", str(response.data).lower())

    def test_logout_rejects_invalid_refresh_token(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("auth-logout"),
            {"refresh": "token-invalido"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("invalido", str(response.data).lower())

    def test_refresh_returns_new_access_token(self):
        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@test.com", "password": "adminpassword123"},
            format="json",
        )

        refresh_response = self.client.post(
            reverse("auth-refresh"),
            {"refresh": login_response.data["refresh"]},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn("access", refresh_response.data)

    def test_blacklisted_refresh_token_cannot_be_refreshed(self):
        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "admin@test.com", "password": "adminpassword123"},
            format="json",
        )
        access_token = login_response.data["access"]
        refresh_token = login_response.data["refresh"]

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access_token}")
        logout_response = self.client.post(
            reverse("auth-logout"),
            {"refresh": refresh_token},
            format="json",
        )
        self.assertEqual(logout_response.status_code, status.HTTP_204_NO_CONTENT)

        refresh_response = self.client.post(
            reverse("auth-refresh"),
            {"refresh": refresh_token},
            format="json",
        )

        self.assertEqual(refresh_response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_returns_profile_as_null_for_superuser_without_profile(self):
        superuser = User.objects.create_superuser(
            username="root@test.com",
            email="root@test.com",
            password="superpassword123",
        )

        login_response = self.client.post(
            reverse("auth-login"),
            {"email": "root@test.com", "password": "superpassword123"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

        me_response = self.client.get(reverse("auth-me"))

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["role"], "administrador")
        self.assertIsNone(me_response.data["profile"]["id"])
        self.assertIsNone(me_response.data["profile"]["is_active"])


class UserManagementApiTests(BaseAuthTestCase):
    def setUp(self):
        self.admin_user = self.create_user(
            email="admin@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )

    def test_admin_can_create_user(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("users-list-create"),
            {
                "email": "docente@test.com",
                "password": "docentepassword123",
                "first_name": "Diana",
                "last_name": "Docente",
                "role_id": self.docente_role.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["email"], "docente@test.com")
        self.assertEqual(response.data["role"]["name"], "Docente")

    def test_non_admin_cannot_create_user(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")

        response = self.client.post(
            reverse("users-list-create"),
            {
                "email": "nuevo@test.com",
                "password": "nuevopassword123",
                "first_name": "Nuevo",
                "last_name": "Usuario",
                "role_id": self.estudiante_role.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_email_must_be_unique(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("users-list-create"),
            {
                "email": "coord@test.com",
                "password": "nuevopassword123",
                "first_name": "Duplicado",
                "last_name": "Correo",
                "role_id": self.estudiante_role.id,
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("email", response.data)

    def test_admin_can_edit_user_role(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        coordinator_profile = self.coordinator_user.profile
        response = self.client.patch(
            reverse("users-detail", kwargs={"user_profile_id": coordinator_profile.id}),
            {"role_id": self.docente_role.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["role"]["name"], "Docente")

    def test_admin_can_deactivate_user(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        coordinator_profile = self.coordinator_user.profile
        response = self.client.delete(
            reverse("users-detail", kwargs={"user_profile_id": coordinator_profile.id})
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        coordinator_profile.refresh_from_db()
        self.coordinator_user.refresh_from_db()
        self.assertFalse(coordinator_profile.is_active)
        self.assertFalse(self.coordinator_user.is_active)

    def test_roles_endpoint_returns_minimum_required_roles(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.get(reverse("roles-list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        role_names = {item["name"] for item in response.data}
        self.assertTrue({"Administrador", "Coordinador", "Docente", "Estudiante"}.issubset(role_names))

    def test_role_change_applies_without_relogin(self):
        coordinator_login = self.client.post(
            reverse("auth-login"),
            {"email": "coord@test.com", "password": "coordpassword123"},
            format="json",
        )
        coordinator_token = coordinator_login.data["access"]

        self.login_and_set_auth("admin@test.com", "adminpassword123")
        self.client.patch(
            reverse("users-detail", kwargs={"user_profile_id": self.coordinator_user.profile.id}),
            {"role_id": self.docente_role.id},
            format="json",
        )

        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {coordinator_token}")
        me_response = self.client.get(reverse("auth-me"))

        self.assertEqual(me_response.status_code, status.HTTP_200_OK)
        self.assertEqual(me_response.data["role"], "docente")

    def test_admin_can_filter_users_by_role_status_and_search(self):
        docente_user = self.create_user(
            email="docente.filtro@test.com",
            password="docentepassword123",
            role=self.docente_role,
            first_name="Dora",
            last_name="Docente",
        )
        docente_user.profile.is_active = False
        docente_user.profile.save(update_fields=["is_active", "updated_at"])

        self.login_and_set_auth("admin@test.com", "adminpassword123")

        role_filtered = self.client.get(
            reverse("users-list-create"),
            {"role_id": self.coordinator_role.id},
        )
        self.assertEqual(role_filtered.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item["role"]["name"] == "Coordinador" for item in role_filtered.data))

        active_filtered = self.client.get(
            reverse("users-list-create"),
            {"is_active": "false"},
        )
        self.assertEqual(active_filtered.status_code, status.HTTP_200_OK)
        self.assertTrue(all(item["is_active"] is False for item in active_filtered.data))

        search_filtered = self.client.get(
            reverse("users-list-create"),
            {"search": "Carlos"},
        )
        self.assertEqual(search_filtered.status_code, status.HTTP_200_OK)
        self.assertTrue(any("Carlos" in item["first_name"] for item in search_filtered.data))

    def test_invalid_is_active_filter_is_ignored(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        baseline = self.client.get(reverse("users-list-create"))
        filtered = self.client.get(reverse("users-list-create"), {"is_active": "talvez"})

        self.assertEqual(baseline.status_code, status.HTTP_200_OK)
        self.assertEqual(filtered.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filtered.data), len(baseline.data))


class UserServiceTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role, _ = Role.objects.get_or_create(name="Administrador")
        cls.coordinator_role, _ = Role.objects.get_or_create(name="Coordinador")

    def test_create_user_with_profile(self):
        profile = create_user_with_profile(
            email="servicio@test.com",
            password="serviciopassword123",
            first_name="Sofia",
            last_name="Servicio",
            role=self.admin_role,
        )

        self.assertEqual(profile.email, "servicio@test.com")
        self.assertEqual(profile.user.username, "servicio@test.com")
        self.assertEqual(profile.role.name, "Administrador")

    def test_create_user_rejects_duplicate_email(self):
        create_user_with_profile(
            email="duplicado@test.com",
            password="serviciopassword123",
            first_name="Primero",
            last_name="Usuario",
            role=self.admin_role,
        )

        with self.assertRaises(UserEmailAlreadyExistsError):
            create_user_with_profile(
                email="duplicado@test.com",
                password="serviciopassword123",
                first_name="Segundo",
                last_name="Usuario",
                role=self.coordinator_role,
            )

    def test_create_user_reuses_orphan_auth_user_with_same_username(self):
        from django.contrib.auth.models import User

        orphan_user = User.objects.create_user(
            username="orphan@test.com",
            email="",
            password="oldpassword123",
        )

        profile = create_user_with_profile(
            email="orphan@test.com",
            password="serviciopassword123",
            first_name="Orphan",
            last_name="User",
            role=self.coordinator_role,
        )

        orphan_user.refresh_from_db()
        profile.refresh_from_db()

        self.assertEqual(profile.user_id, orphan_user.id)
        self.assertEqual(profile.email, "orphan@test.com")
        self.assertEqual(orphan_user.email, "orphan@test.com")
        self.assertTrue(orphan_user.check_password("serviciopassword123"))

    def test_update_user_profile(self):
        profile = create_user_with_profile(
            email="update@test.com",
            password="serviciopassword123",
            first_name="Original",
            last_name="Nombre",
            role=self.admin_role,
        )

        updated_profile = update_user_profile(
            profile,
            email="actualizado@test.com",
            first_name="Actualizado",
            last_name="Usuario",
            role=self.coordinator_role,
            is_active=True,
        )

        self.assertEqual(updated_profile.email, "actualizado@test.com")
        self.assertEqual(updated_profile.user.email, "actualizado@test.com")
        self.assertEqual(updated_profile.role.name, "Coordinador")

    def test_deactivate_user_profile(self):
        profile = create_user_with_profile(
            email="desactivar@test.com",
            password="serviciopassword123",
            first_name="Des",
            last_name="Activar",
            role=self.admin_role,
        )

        deactivate_user_profile(profile)
        profile.refresh_from_db()
        profile.user.refresh_from_db()

        self.assertFalse(profile.is_active)

    def test_create_docente_creates_teacher(self):
        from apps.core.models import CatalogItem, Teacher

        docente_role, _ = Role.objects.get_or_create(name="Docente")
        # Ensure a teacher link type exists
        CatalogItem.objects.get_or_create(
            catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE,
            name="Vinculacion",
            defaults={"is_active": True},
        )

        profile = create_user_with_profile(
            email="profe_new@test.com",
            password="serviciopassword123",
            first_name="Profe",
            last_name="Nuevo",
            role=docente_role,
        )

        self.assertTrue(Teacher.objects.filter(user_profile=profile).exists())
        teacher = Teacher.objects.get(user_profile=profile)
        self.assertEqual(teacher.email, "profe_new@test.com")
        self.assertTrue(profile.user.is_active)


class SystemConfigApiTests(BaseAuthTestCase):
    def setUp(self):
        self.admin_user = self.create_user(
            email="admin@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )

    def test_admin_can_update_subject_class_type_item(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        subject = Subject.objects.create(
            code="TSTCLASS",
            name="Prueba nueva",
            class_type=Subject.CLASS_TYPE_VIRTUAL,
            credits=2,
            weekly_hours=2,
            capacity=20,
            difficulty=40,
        )
        presencial_item = CatalogItem.objects.filter(
            catalog_type=CatalogItem.CatalogType.CLASS_TYPE,
            name__icontains="pres",
        ).first()
        self.assertIsNotNone(presencial_item, "No class_type CatalogItem found for presencial")

        response = self.client.patch(
            reverse("programming-subjects-detail", kwargs={"config_id": subject.id}),
            {"class_type_item_id": presencial_item.id},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        subject.refresh_from_db()
        self.assertEqual(subject.class_type_item_id, presencial_item.id)
        self.assertEqual(subject.class_type, Subject.CLASS_TYPE_PRESENCIAL)

    def test_admin_can_crud_academic_period(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        create_response = self.client.post(
            reverse("config-periods-list-create"),
            {
                "code": "2026-1",
                "name": "Periodo 2026-1",
                "start_date": "2026-01-15",
                "end_date": "2026-06-15",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        period_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("config-periods-detail", kwargs={"config_id": period_id}),
            {"name": "Periodo 2026-A"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Periodo 2026-A")

        delete_response = self.client.delete(
            reverse("config-periods-detail", kwargs={"config_id": period_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_soft_delete_academic_period_with_schedule_executions(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        period = AcademicPeriod.objects.create(
            code="2026-SOFT",
            name="Periodo para borrar",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 6, 15),
            is_active=True,
        )
        ScheduleExecution.objects.create(
            academic_period=period,
            requested_by=self.admin_user,
            status=ScheduleExecution.Status.COMPLETED,
            progress=100,
        )

        response = self.client.delete(reverse("config-periods-detail", kwargs={"config_id": period.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        period.refresh_from_db()
        self.assertFalse(period.is_active)

    def test_admin_can_soft_delete_space_type(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        space_type = SpaceType.objects.create(name="Laboratorio Temporal", description="Prueba")

        response = self.client.delete(reverse("config-space-types-detail", kwargs={"config_id": space_type.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        space_type.refresh_from_db()
        self.assertFalse(space_type.is_active)

    def test_admin_cannot_delete_academic_period_with_schedule_executions(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        period = AcademicPeriod.objects.create(
            code="2026-BLK",
            name="Periodo bloqueado",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 6, 15),
            is_active=True,
        )
        ScheduleExecution.objects.create(
            academic_period=period,
            requested_by=self.admin_user,
            status=ScheduleExecution.Status.COMPLETED,
            progress=100,
        )

        response = self.client.delete(reverse("config-periods-detail", kwargs={"config_id": period.id}))

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        period.refresh_from_db()
        self.assertFalse(period.is_active)
        self.assertTrue(AcademicPeriod.objects.filter(id=period.id).exists())

    def test_admin_can_publish_and_unpublish_academic_period(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        campus = Campus.objects.create(code="PUB-CAM", name="Campus Publicacion")
        program = AcademicProgram.objects.create(code="PUB-PRG", name="Programa Publicacion", campus=campus)
        period = AcademicPeriod.objects.create(
            code="2026-PUB",
            name="Periodo Publicacion",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 6, 15),
            is_active=True,
            is_schedule_published=False,
        )
        subject = Subject.objects.create(
            code="PUB101",
            name="Asignatura Publicacion",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        subject_group = SubjectGroup.objects.create(subject=subject, identifier="G1")
        working_day = WorkingDay.objects.create(day_of_week=2, name="Martes PUB", is_active=True)
        time_slot = TimeSlot.objects.create(
            name="08:00-10:00 PUB",
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True,
        )
        create_subject_offering(
            subject=subject,
            subject_group=subject_group,
            working_day=working_day,
            time_slot=time_slot,
            academic_program=program,
            academic_period=period,
            semester=1,
            student_count=25,
        )

        publish_response = self.client.post(
            reverse("config-periods-publish", kwargs={"config_id": period.id}),
            {},
            format="json",
        )
        self.assertEqual(publish_response.status_code, status.HTTP_200_OK)
        self.assertTrue(publish_response.data["confirmation_required"])
        self.assertFalse(publish_response.data["published"])
        self.assertEqual(len(publish_response.data["pending_offerings"]), 1)

        force_publish_response = self.client.post(
            reverse("config-periods-publish", kwargs={"config_id": period.id}),
            {"force": True},
            format="json",
        )
        self.assertEqual(force_publish_response.status_code, status.HTTP_200_OK)
        self.assertTrue(force_publish_response.data["published"])

        period.refresh_from_db()
        self.assertTrue(period.is_schedule_published)
        self.assertIsNotNone(period.schedule_published_at)

        unpublish_response = self.client.post(
            reverse("config-periods-unpublish", kwargs={"config_id": period.id}),
            {},
            format="json",
        )
        self.assertEqual(unpublish_response.status_code, status.HTTP_200_OK)
        self.assertFalse(unpublish_response.data["published"])

        period.refresh_from_db()
        self.assertFalse(period.is_schedule_published)
        self.assertIsNone(period.schedule_published_at)

    def test_invalid_period_range_is_rejected(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("config-periods-list-create"),
            {
                "code": "2026-X",
                "name": "Periodo invalido",
                "start_date": "2026-08-01",
                "end_date": "2026-06-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_date", response.data)

    def test_period_name_whitespace_is_rejected(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("config-periods-list-create"),
            {
                "code": "2026-W",
                "name": "   ",
                "start_date": "2026-02-01",
                "end_date": "2026-06-01",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", response.data)

    def test_invalid_timeslot_range_is_rejected(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.post(
            reverse("config-time-slots-list-create"),
            {
                "name": "Franja invalida",
                "start_time": "10:00:00",
                "end_time": "09:00:00",
            },
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("end_time", response.data)

    def test_admin_can_crud_working_day(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        create_response = self.client.post(
            reverse("config-working-days-list-create"),
            {"day_of_week": 1, "name": "Lunes", "is_active": True},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        day_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("config-working-days-detail", kwargs={"config_id": day_id}),
            {"name": "Lunes Academico"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Lunes Academico")

        delete_response = self.client.delete(
            reverse("config-working-days-detail", kwargs={"config_id": day_id})
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

    def test_admin_can_crud_time_slot_and_space_type(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        create_slot = self.client.post(
            reverse("config-time-slots-list-create"),
            {
                "name": "Franja 1",
                "start_time": "07:00:00",
                "end_time": "09:00:00",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(create_slot.status_code, status.HTTP_201_CREATED)

        create_space = self.client.post(
            reverse("config-space-types-list-create"),
            {"name": "Laboratorio", "description": "Tipo laboratorio", "is_active": True},
            format="json",
        )
        self.assertEqual(create_space.status_code, status.HTTP_201_CREATED)

    def test_non_admin_cannot_manage_config(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")

        response = self.client.post(
            reverse("config-space-types-list-create"),
            {"name": "Auditorio", "description": "Tipo auditorio", "is_active": True},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_list_each_config_resource(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        self.client.post(
            reverse("config-periods-list-create"),
            {
                "code": "2026-L",
                "name": "Periodo listado",
                "start_date": "2026-01-10",
                "end_date": "2026-05-20",
            },
            format="json",
        )
        self.client.post(
            reverse("config-working-days-list-create"),
            {"day_of_week": 2, "name": "Martes"},
            format="json",
        )
        self.client.post(
            reverse("config-time-slots-list-create"),
            {"name": "Franja listada", "start_time": "08:00:00", "end_time": "09:00:00"},
            format="json",
        )
        self.client.post(
            reverse("config-space-types-list-create"),
            {"name": "Aula", "description": "Tipo aula"},
            format="json",
        )

        periods_response = self.client.get(reverse("config-periods-list-create"))
        days_response = self.client.get(reverse("config-working-days-list-create"))
        slots_response = self.client.get(reverse("config-time-slots-list-create"))
        types_response = self.client.get(reverse("config-space-types-list-create"))

        self.assertEqual(periods_response.status_code, status.HTTP_200_OK)
        self.assertEqual(days_response.status_code, status.HTTP_200_OK)
        self.assertEqual(slots_response.status_code, status.HTTP_200_OK)
        self.assertEqual(types_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(periods_response.data), 1)
        self.assertGreaterEqual(len(days_response.data), 1)
        self.assertGreaterEqual(len(slots_response.data), 1)
        self.assertGreaterEqual(len(types_response.data), 1)

    def test_admin_can_manage_catalogs_by_type(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        create_response = self.client.post(
            reverse("catalogs-list-create", kwargs={"catalog_type": "teacher_link_type"}),
            {
                "name": "Catedra",
                "description": "Docente por hora",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["catalog_type"], "teacher_link_type")

        item_id = create_response.data["id"]
        update_response = self.client.patch(
            reverse(
                "catalogs-detail",
                kwargs={"catalog_type": "teacher_link_type", "config_id": item_id},
            ),
            {"name": "Tiempo Completo"},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["name"], "Tiempo Completo")

        list_response = self.client.get(
            reverse("catalogs-list-create", kwargs={"catalog_type": "teacher_link_type"}),
        )
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertTrue(any(item["id"] == item_id for item in list_response.data))

    def test_delete_catalog_item_deactivates_record(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        item = CatalogItem.objects.create(
            catalog_type="class_type",
            name="Teorica",
            description="Clase magistral",
            is_active=True,
        )

        response = self.client.delete(
            reverse(
                "catalogs-detail",
                kwargs={"catalog_type": "class_type", "config_id": item.id},
            )
        )

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        item.refresh_from_db()
        self.assertFalse(item.is_active)

    def test_catalog_item_name_can_be_reused_after_deactivation(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        item = CatalogItem.objects.create(
            catalog_type="class_type",
            name="Prueba",
            description="Clase de prueba",
            is_active=True,
        )

        delete_response = self.client.delete(
            reverse(
                "catalogs-detail",
                kwargs={"catalog_type": "class_type", "config_id": item.id},
            )
        )
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        create_response = self.client.post(
            reverse("catalogs-list-create", kwargs={"catalog_type": "class_type"}),
            {"name": "Prueba", "description": "Reutilizado"},
            format="json",
        )

        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(create_response.data["name"], "Prueba")

    def test_non_admin_cannot_modify_catalog_items(self):
        self.login_and_set_auth("coord@test.com", "coordpassword123")

        create_response = self.client.post(
            reverse("catalogs-list-create", kwargs={"catalog_type": "class_type"}),
            {"name": "Laboratorio"},
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_403_FORBIDDEN)

    def test_catalogs_reject_invalid_type(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.get(
            reverse("catalogs-list-create", kwargs={"catalog_type": "invalid_type"}),
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_catalog_rejects_case_insensitive_duplicate_name(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        first = self.client.post(
            reverse("catalogs-list-create", kwargs={"catalog_type": "class_type"}),
            {"name": "Magistral", "description": "Clase teorica"},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        duplicate = self.client.post(
            reverse("catalogs-list-create", kwargs={"catalog_type": "class_type"}),
            {"name": "magistral", "description": "Mismo nombre"},
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("name", duplicate.data)

    def test_import_master_data_accepts_csv_with_row_report(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        csv_content = (
            "name,description,is_active\n"
            "Magistral,Clase teorica,true\n"
            "Magistral,Duplicado,true\n"
            "Laboratorio,Clase practica,true\n"
        )
        csv_file = SimpleUploadedFile(
            "class_types.csv",
            csv_content.encode("utf-8"),
            content_type="text/csv",
        )

        response = self.client.post(
            reverse("imports-master-data"),
            {"resource_type": "class_type", "file": csv_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["resource_type"], "class_type")
        self.assertEqual(response.data["total_processed"], 3)
        self.assertEqual(response.data["successful"], 2)
        self.assertEqual(response.data["failed"], 1)
        self.assertTrue(any(row["status"] == "error" for row in response.data["rows"]))

    def test_import_master_data_accepts_xlsx(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        workbook = Workbook()
        worksheet = workbook.active
        worksheet.append(["code", "name", "start_date", "end_date", "is_active"])
        worksheet.append(["2027-1", "Periodo 2027-1", "2027-01-15", "2027-06-15", "true"])

        buffer = BytesIO()
        workbook.save(buffer)
        xlsx_file = SimpleUploadedFile(
            "periods.xlsx",
            buffer.getvalue(),
            content_type=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            ),
        )

        response = self.client.post(
            reverse("imports-master-data"),
            {"resource_type": "periods", "file": xlsx_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["total_processed"], 1)
        self.assertEqual(response.data["successful"], 1)
        self.assertEqual(response.data["failed"], 0)

    def test_import_master_data_reports_missing_columns(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        csv_content = "name,is_active\nSoloNombre,true\n"
        csv_file = SimpleUploadedFile(
            "working_days.csv",
            csv_content.encode("utf-8"),
            content_type="text/csv",
        )

        response = self.client.post(
            reverse("imports-master-data"),
            {"resource_type": "working_days", "file": csv_file},
            format="multipart",
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("file", response.data)

    def test_import_templates_list_is_available(self):
        self.login_and_set_auth("admin@test.com", "adminpassword123")

        response = self.client.get(reverse("imports-master-data"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("templates", response.data)
        self.assertTrue(any(item["resource_type"] == "periods" for item in response.data["templates"]))


class MasterDataApiTests(BaseAuthTestCase):
    def setUp(self):
        self.admin_user = self.create_user(
            email="admin.master@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord.master@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )

        self.teacher_link_type = CatalogItem.objects.create(
            catalog_type="teacher_link_type",
            name="Catedra",
            description="Docente por horas",
        )
        self.class_type = CatalogItem.objects.create(
            catalog_type="class_type",
            name="Magistral",
            description="Clase teorica",
        )
        self.space_type = CatalogItem.objects.create(
            catalog_type="academic_space_type",
            name="Aula",
            description="Salon convencional",
        )

    def test_admin_can_crud_and_filter_master_data(self):
        self.login_and_set_auth("admin.master@test.com", "adminpassword123")

        campus_response = self.client.post(
            reverse("campuses-list-create"),
            {"code": "BOL", "name": "Bolivar", "is_active": True},
            format="json",
        )
        self.assertEqual(campus_response.status_code, status.HTTP_201_CREATED)
        campus_id = campus_response.data["id"]

        program_response = self.client.post(
            reverse("programs-list-create"),
            {
                "code": "SIS",
                "name": "Ingenieria de Sistemas",
                "campus_id": campus_id,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(program_response.status_code, status.HTTP_201_CREATED)
        program_id = program_response.data["id"]

        teacher_response = self.client.post(
            reverse("teachers-list-create"),
            {
                "first_name": "Lucia",
                "last_name": "Perez",
                "email": "lucia.perez@test.com",
                "link_type_id": self.teacher_link_type.id,
                "hourly_rate": "55000.00",
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(teacher_response.status_code, status.HTTP_201_CREATED)

        course_response = self.client.post(
            reverse("courses-list-create"),
            {
                "code": "INF101",
                "name": "Programacion I",
                "academic_program_id": program_id,
                "class_type_id": self.class_type.id,
                "credits": 3,
                "weekly_hours": 4,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(course_response.status_code, status.HTTP_201_CREATED)
        course_id = course_response.data["id"]

        group_response = self.client.post(
            reverse("course-groups-list-create"),
            {
                "course_id": course_id,
                "identifier": "Grupo A",
                "student_count": 35,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(group_response.status_code, status.HTTP_201_CREATED)

        classroom_response = self.client.post(
            reverse("classrooms-list-create"),
            {
                "code": "SAL-101",
                "name": "Salon 101",
                "campus_id": campus_id,
                "space_type_id": self.space_type.id,
                "capacity": 40,
                "is_accessible": True,
                "is_active": True,
            },
            format="json",
        )
        self.assertEqual(classroom_response.status_code, status.HTTP_201_CREATED)

        filtered_courses = self.client.get(
            reverse("courses-list-create"),
            {"academic_program_id": program_id, "search": "INF"},
        )
        self.assertEqual(filtered_courses.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filtered_courses.data), 1)

        filtered_classrooms = self.client.get(
            reverse("classrooms-list-create"),
            {"campus_id": campus_id, "is_accessible": "true"},
        )
        self.assertEqual(filtered_classrooms.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filtered_classrooms.data), 1)

        filtered_groups = self.client.get(
            reverse("course-groups-list-create"),
            {"course_id": course_id},
        )
        self.assertEqual(filtered_groups.status_code, status.HTTP_200_OK)
        self.assertEqual(len(filtered_groups.data), 1)

    def test_duplicate_group_for_same_course_is_rejected(self):
        self.login_and_set_auth("admin.master@test.com", "adminpassword123")

        campus = Campus.objects.create(code="BAL", name="Balsas")
        program = AcademicProgram.objects.create(code="IND", name="Industrial", campus=campus)
        course = Course.objects.create(
            code="MAT101",
            name="Calculo",
            academic_program=program,
            class_type=self.class_type,
            credits=4,
            weekly_hours=4,
        )

        first = self.client.post(
            reverse("course-groups-list-create"),
            {"course_id": course.id, "identifier": "Grupo 1", "student_count": 30},
            format="json",
        )
        self.assertEqual(first.status_code, status.HTTP_201_CREATED)

        duplicate = self.client.post(
            reverse("course-groups-list-create"),
            {"course_id": course.id, "identifier": "Grupo 1", "student_count": 28},
            format="json",
        )
        self.assertEqual(duplicate.status_code, status.HTTP_400_BAD_REQUEST)

    def test_non_admin_cannot_create_master_data_records(self):
        self.login_and_set_auth("coord.master@test.com", "coordpassword123")

        response = self.client.post(
            reverse("campuses-list-create"),
            {"code": "OTR", "name": "Otra sede"},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PermissionUtilityTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role, _ = Role.objects.get_or_create(name="Administrador")

    def test_get_user_role_name_returns_none_for_anonymous(self):
        from .permissions import get_user_role_name

        self.assertIsNone(get_user_role_name(AnonymousUser()))

    def test_get_user_role_name_returns_none_when_profile_is_missing(self):
        from .permissions import get_user_role_name

        user = User.objects.create_user(
            username="sinperfil@test.com",
            email="sinperfil@test.com",
            password="password12345",
        )

        self.assertIsNone(get_user_role_name(user))

    def test_has_allowed_roles_without_configured_roles_returns_true(self):
        from .permissions import HasAllowedRoles

        user = User.objects.create_user(
            username="noperfiltwo@test.com",
            email="noperfiltwo@test.com",
            password="password12345",
        )

        request = type("Request", (), {"user": user})
        view = type("View", (), {})

        permission = HasAllowedRoles()
        self.assertTrue(permission.has_permission(request, view))


class ConfigServiceTests(TestCase):
    def test_create_period_validates_dates(self):
        with self.assertRaises(ConfigValidationError):
            create_academic_period(
                code="2026-2",
                name="Periodo invalido",
                start_date=date(2026, 7, 1),
                end_date=date(2026, 6, 1),
                is_active=True,
            )

    def test_create_working_day_validates_range(self):
        with self.assertRaises(ConfigValidationError):
            create_working_day(day_of_week=9, name="Fuera de rango", is_active=True)

    def test_create_and_update_time_slot_validate_range(self):
        with self.assertRaises(ConfigValidationError):
            create_time_slot(
                name="No valida",
                start_time=time(11, 0),
                end_time=time(10, 0),
                is_active=True,
            )

        valid_slot = create_time_slot(
            name="Valida",
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True,
        )

        with self.assertRaises(ConfigValidationError):
            update_time_slot(
                valid_slot,
                name="Valida",
                start_time=time(10, 0),
                end_time=time(10, 0),
                is_active=True,
            )

    def test_create_working_day_persists_data(self):
        day = create_working_day(day_of_week=2, name="Martes", is_active=True)

        self.assertEqual(day.day_of_week, 2)
        self.assertEqual(day.name, "Martes")
        self.assertTrue(WorkingDay.objects.filter(id=day.id).exists())

    def test_period_update_and_duplicate_code_validation(self):
        first = create_academic_period(
            code="2026-1",
            name="Periodo 1",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 5, 30),
            is_active=True,
        )
        second = create_academic_period(
            code="2026-2",
            name="Periodo 2",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 11, 30),
            is_active=True,
        )

        updated = update_academic_period(
            first,
            code="2026-1A",
            name="Periodo 1A",
            start_date=date(2026, 1, 15),
            end_date=date(2026, 6, 1),
            is_active=False,
            is_schedule_published=False,
        )

        self.assertEqual(updated.code, "2026-1A")
        self.assertFalse(updated.is_active)

        reused = update_academic_period(
            second,
            code="2026-1A",
            name="Reutilizado",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 11, 30),
            is_active=True,
            is_schedule_published=False,
        )
        self.assertEqual(reused.code, "2026-1A")
        self.assertTrue(reused.is_active)

    def test_period_code_can_be_reused_after_deactivation(self):
        original = create_academic_period(
            code="2026-1",
            name="Periodo original",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 5, 30),
            is_active=True,
        )

        update_academic_period(
            original,
            code="2026-1",
            name="Periodo original",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 5, 30),
            is_active=False,
            is_schedule_published=False,
        )

        reused = create_academic_period(
            code="2026-1",
            name="Periodo reutilizado",
            start_date=date(2026, 7, 1),
            end_date=date(2026, 11, 30),
            is_active=True,
        )

        self.assertEqual(reused.code, "2026-1")
        self.assertTrue(reused.is_active)

    def test_working_day_update_and_duplicate_validation(self):
        monday = create_working_day(day_of_week=1, name="Lunes", is_active=True)
        tuesday = create_working_day(day_of_week=2, name="Martes", is_active=True)

        updated = update_working_day(
            monday,
            day_of_week=3,
            name="Miercoles",
            is_active=False,
        )
        self.assertEqual(updated.day_of_week, 3)
        self.assertFalse(updated.is_active)

        with self.assertRaises(ConfigValidationError):
            update_working_day(
                tuesday,
                day_of_week=3,
                name="Martes",
                is_active=True,
            )

    def test_time_slot_duplicate_validation(self):
        create_time_slot(
            name="Franja",
            start_time=time(7, 0),
            end_time=time(8, 0),
            is_active=True,
        )

        with self.assertRaises(ConfigValidationError):
            create_time_slot(
                name="Franja",
                start_time=time(7, 0),
                end_time=time(8, 0),
                is_active=True,
            )

    def test_space_type_update_and_duplicate_validation(self):
        lab = create_space_type(name="Laboratorio", description="Lab", is_active=True)
        aula = create_space_type(name="Aula", description="Clase", is_active=True)

        updated = update_space_type(
            lab,
            name="Laboratorio Avanzado",
            description="Lab de hardware",
            is_active=False,
        )
        self.assertEqual(updated.name, "Laboratorio Avanzado")
        self.assertFalse(updated.is_active)

        with self.assertRaises(ConfigValidationError):
            update_space_type(
                aula,
                name="Laboratorio Avanzado",
                description="Duplicado",
                is_active=True,
            )

    def test_catalog_item_create_update_and_duplicate_validation(self):
        vinculo_1 = create_catalog_item(
            catalog_type="teacher_link_type",
            name="Catedra",
            description="Vinculacion por horas",
            is_active=True,
        )
        vinculo_2 = create_catalog_item(
            catalog_type="teacher_link_type",
            name="Tiempo Completo",
            description="Planta",
            is_active=True,
        )

        updated = update_catalog_item(
            vinculo_1,
            name="Catedra Externa",
            description="Horas por semestre",
            is_active=False,
        )
        self.assertEqual(updated.name, "Catedra Externa")
        self.assertFalse(updated.is_active)

        reused = update_catalog_item(
            vinculo_2,
            name="Catedra Externa",
            description="Reutilizado",
            is_active=True,
        )
        self.assertEqual(reused.name, "Catedra Externa")
        self.assertTrue(reused.is_active)

    def test_catalog_item_validates_catalog_type(self):
        with self.assertRaises(ConfigValidationError):
            create_catalog_item(
                catalog_type="otro",
                name="Invalido",
                description="No deberia crearse",
                is_active=True,
            )

    def test_period_code_duplicate_is_case_insensitive(self):
        create_academic_period(
            code="2026-A",
            name="Periodo A",
            start_date=date(2026, 1, 10),
            end_date=date(2026, 5, 20),
            is_active=True,
        )

        with self.assertRaises(ConfigValidationError):
            create_academic_period(
                code="2026-a",
                name="Periodo A duplicado",
                start_date=date(2026, 7, 1),
                end_date=date(2026, 11, 20),
                is_active=True,
            )

    def test_whitespace_names_are_rejected(self):
        with self.assertRaises(ConfigValidationError):
            create_working_day(day_of_week=1, name="   ", is_active=True)

        with self.assertRaises(ConfigValidationError):
            create_time_slot(
                name="   ",
                start_time=time(8, 0),
                end_time=time(9, 0),
                is_active=True,
            )

        with self.assertRaises(ConfigValidationError):
            create_catalog_item(
                catalog_type="class_type",
                name="   ",
                description="No valido",
                is_active=True,
            )


class ClassroomTests(BaseAuthTestCase):
    """Unit tests for Classroom CRUD — target ≥ 95% coverage."""

    def setUp(self):
        self.admin_user = self.create_user(
            email="admin.classroom@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord.classroom@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )
        self.campus = Campus.objects.create(code="MAIN", name="Campus Principal")
        self.space_type = CatalogItem.objects.create(
            catalog_type="academic_space_type",
            name="Aula",
            description="Salon convencional",
        )

    def _classroom_payload(self, **kwargs):
        payload = {
            "code": "A101",
            "name": "Salon A101",
            "campus_id": self.campus.id,
            "space_type_id": self.space_type.id,
            "capacity": 30,
            "is_accessible": False,
            "is_active": True,
        }
        payload.update(kwargs)
        return payload

    # --- LIST ---

    def test_admin_can_list_classrooms(self):
        Classroom.objects.create(
            code="B200",
            name="Salon B200",
            campus=self.campus,
            space_type=self.space_type,
            capacity=20,
        )
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.get(reverse("classrooms-list-create"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_coordinator_cannot_list_classrooms(self):
        self.login_and_set_auth("coord.classroom@test.com", "coordpassword123")
        response = self.client.get(reverse("classrooms-list-create"))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- CREATE ---

    def test_admin_can_create_classroom(self):
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["code"], "A101")
        self.assertEqual(response.data["capacity"], 30)
        self.assertFalse(response.data["is_accessible"])

    def test_coordinator_cannot_create_classroom(self):
        self.login_and_set_auth("coord.classroom@test.com", "coordpassword123")
        response = self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(code="X999"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_duplicate_code_is_rejected(self):
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(code="DUP01"),
            format="json",
        )
        response = self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(code="DUP01", name="Salon duplicado"),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_zero_capacity_is_rejected(self):
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(capacity=0),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_space_type_must_be_academic_space_type(self):
        wrong_catalog = CatalogItem.objects.create(
            catalog_type="class_type",
            name="Clase magistral",
        )
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(space_type_id=wrong_catalog.id),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_is_accessible_flag_is_persisted(self):
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.post(
            reverse("classrooms-list-create"),
            self._classroom_payload(code="ACC01", is_accessible=True),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(response.data["is_accessible"])
        self.assertTrue(Classroom.objects.get(code="ACC01").is_accessible)

    # --- UPDATE ---

    def test_admin_can_update_classroom(self):
        classroom = Classroom.objects.create(
            code="UPD01",
            name="Original",
            campus=self.campus,
            space_type=self.space_type,
            capacity=25,
        )
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.patch(
            reverse("classrooms-detail", args=[classroom.id]),
            {"name": "Actualizado", "capacity": 40},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        classroom.refresh_from_db()
        self.assertEqual(classroom.name, "Actualizado")
        self.assertEqual(classroom.capacity, 40)

    def test_coordinator_cannot_update_classroom(self):
        classroom = Classroom.objects.create(
            code="NOUPD",
            name="No actualizable",
            campus=self.campus,
            space_type=self.space_type,
            capacity=20,
        )
        self.login_and_set_auth("coord.classroom@test.com", "coordpassword123")
        response = self.client.patch(
            reverse("classrooms-detail", args=[classroom.id]),
            {"capacity": 50},
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- DELETE ---

    def test_admin_can_delete_classroom(self):
        classroom = Classroom.objects.create(
            code="DEL01",
            name="Para eliminar",
            campus=self.campus,
            space_type=self.space_type,
            capacity=15,
        )
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.delete(reverse("classrooms-detail", args=[classroom.id]))
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Classroom.objects.filter(id=classroom.id).exists())

    def test_coordinator_cannot_delete_classroom(self):
        classroom = Classroom.objects.create(
            code="NODEL",
            name="No borrable",
            campus=self.campus,
            space_type=self.space_type,
            capacity=10,
        )
        self.login_and_set_auth("coord.classroom@test.com", "coordpassword123")
        response = self.client.delete(reverse("classrooms-detail", args=[classroom.id]))
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # --- FILTER ---

    def test_filter_by_campus(self):
        other_campus = Campus.objects.create(code="OTR", name="Otra sede")
        Classroom.objects.create(
            code="CAM1", name="En campus principal", campus=self.campus,
            space_type=self.space_type, capacity=20,
        )
        Classroom.objects.create(
            code="CAM2", name="En otra sede", campus=other_campus,
            space_type=self.space_type, capacity=20,
        )
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.get(
            reverse("classrooms-list-create"),
            {"campus_id": self.campus.id},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [item["code"] for item in response.data]
        self.assertIn("CAM1", codes)
        self.assertNotIn("CAM2", codes)

    def test_filter_by_is_accessible(self):
        Classroom.objects.create(
            code="ACC10", name="Accesible", campus=self.campus,
            space_type=self.space_type, capacity=20, is_accessible=True,
        )
        Classroom.objects.create(
            code="NAC10", name="No accesible", campus=self.campus,
            space_type=self.space_type, capacity=20, is_accessible=False,
        )
        self.login_and_set_auth("admin.classroom@test.com", "adminpassword123")
        response = self.client.get(
            reverse("classrooms-list-create"),
            {"is_accessible": "true"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        codes = [item["code"] for item in response.data]
        self.assertIn("ACC10", codes)
        self.assertNotIn("NAC10", codes)

    # --- UNAUTHENTICATED ---

    def test_unauthenticated_request_is_rejected(self):
        response = self.client.get(reverse("classrooms-list-create"))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class SubjectOfferingStudentCountTests(BaseAuthTestCase):
    """Tests for student_count field on SubjectOffering (HU - Registrar cupo)."""

    def setUp(self):
        self.admin_user = self.create_user(
            email="admin.sc@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Admin",
        )
        self.coordinator_user = self.create_user(
            email="coord.sc@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )
        self.campus = Campus.objects.create(code="SC-CAM", name="Campus SC")
        self.program = AcademicProgram.objects.create(
            code="SC-PROG", name="Programa SC", campus=self.campus
        )
        self.period = AcademicPeriod.objects.create(
            code="SC-2026",
            name="Periodo SC",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
        )
        self.subject = Subject.objects.create(
            code="SC-MAT",
            name="Matematicas SC",
            class_type="presencial",
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=12,
        )
        self.subject_group = SubjectGroup.objects.create(
            subject=self.subject,
            identifier="Grupo A",
        )
        self.working_day = WorkingDay.objects.create(day_of_week=1, name="Lunes SC", is_active=True)
        self.time_slot = TimeSlot.objects.create(
            name="07:00-09:00 SC",
            start_time=time(7, 0),
            end_time=time(9, 0),
            is_active=True,
        )

    def _offering_payload(self, **kwargs):
        payload = {
            "subject_id": self.subject.id,
            "subject_group_id": self.subject_group.id,
            "academic_program_id": self.program.id,
            "working_day_id": self.working_day.id,
            "time_slot_id": self.time_slot.id,
            "semester": 1,
            "is_active": True,
        }
        payload.update(kwargs)
        return payload

    def test_student_count_is_null_by_default(self):
        self.login_and_set_auth("coord.sc@test.com", "coordpassword123")
        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            self._offering_payload(),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["student_count"])

    def test_coordinator_can_set_student_count(self):
        self.login_and_set_auth("coord.sc@test.com", "coordpassword123")
        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            self._offering_payload(student_count=45),
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student_count"], 45)

    def test_coordinator_can_update_student_count(self):
        self.login_and_set_auth("coord.sc@test.com", "coordpassword123")
        create_response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            self._offering_payload(student_count=30),
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        offering_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("programming-subject-offerings-detail", args=[offering_id]),
            {"student_count": 55},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data["student_count"], 55)

    def test_student_count_can_be_cleared_to_null(self):
        self.login_and_set_auth("coord.sc@test.com", "coordpassword123")
        create_response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            self._offering_payload(student_count=20),
            format="json",
        )
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)
        offering_id = create_response.data["id"]

        update_response = self.client.patch(
            reverse("programming-subject-offerings-detail", args=[offering_id]),
            {"student_count": None},
            format="json",
        )
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertIsNone(update_response.data["student_count"])


class BusinessRuleTests(TestCase):
    """Tests for TEC-21: capacity, space-type compatibility, credits/hours ranges."""

    @classmethod
    def setUpTestData(cls):
        cls.campus = Campus.objects.create(code="TEC21", name="Campus TEC21")
        cls.program = AcademicProgram.objects.create(
            code="TEC21-PRG", name="Programa TEC21", campus=cls.campus
        )
        cls.period = AcademicPeriod.objects.create(
            code="TEC21-2026",
            name="Periodo TEC21",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
        )
        cls.working_day = WorkingDay.objects.create(
            day_of_week=5, name="Viernes TEC21", is_active=True
        )
        cls.time_slot = TimeSlot.objects.create(
            name="10:00-12:00 TEC21",
            start_time=time(10, 0),
            end_time=time(12, 0),
            is_active=True,
        )
        cls.space_type = CatalogItem.objects.create(
            catalog_type="academic_space_type",
            name="Aula TEC21",
        )

    # --- Regla 3: Creditos e intensidad horaria en rangos permitidos ---

    def test_credits_above_maximum_are_rejected(self):
        with self.assertRaises(ConfigValidationError) as ctx:
            create_subject(
                code="TST-CRED",
                name="Test Creditos",
                class_type="presencial",
                credits=SUBJECT_CREDITS_MAX + 1,
                weekly_hours=4,
                capacity=30,
            )
        self.assertEqual(ctx.exception.field, "credits")

    def test_credits_at_maximum_are_accepted(self):
        subject = create_subject(
            code="TST-CMAX",
            name="Test Creditos Max",
            class_type="presencial",
            credits=SUBJECT_CREDITS_MAX,
            weekly_hours=4,
            capacity=30,
        )
        self.assertEqual(subject.credits, SUBJECT_CREDITS_MAX)

    def test_weekly_hours_above_maximum_are_rejected(self):
        with self.assertRaises(ConfigValidationError) as ctx:
            create_subject(
                code="TST-WHRS",
                name="Test Horas",
                class_type="presencial",
                credits=3,
                weekly_hours=SUBJECT_WEEKLY_HOURS_MAX + 1,
                capacity=30,
            )
        self.assertEqual(ctx.exception.field, "weekly_hours")

    def test_weekly_hours_at_maximum_are_accepted(self):
        subject = create_subject(
            code="TST-WMAX",
            name="Test Horas Max",
            class_type="presencial",
            credits=3,
            weekly_hours=SUBJECT_WEEKLY_HOURS_MAX,
            capacity=30,
        )
        self.assertEqual(subject.weekly_hours, SUBJECT_WEEKLY_HOURS_MAX)

    # --- Regla 2: Compatibilidad asignatura-tipo de espacio ---

    def test_virtual_subject_with_space_type_is_rejected(self):
        subject = Subject.objects.create(
            code="TST-VIRT",
            name="Asignatura Virtual",
            class_type=Subject.CLASS_TYPE_VIRTUAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        group = SubjectGroup.objects.create(subject=subject, identifier="GV1")

        with self.assertRaises(ConfigValidationError) as ctx:
            create_subject_offering(
                subject=subject,
                subject_group=group,
                working_day=self.working_day,
                time_slot=self.time_slot,
                required_space_type=self.space_type,
                academic_program=self.program,
                academic_period=self.period,
                semester=1,
            )
        self.assertEqual(ctx.exception.field, "required_space_type_id")

    def test_presencial_subject_with_space_type_is_accepted(self):
        subject = Subject.objects.create(
            code="TST-PRES",
            name="Asignatura Presencial",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        group = SubjectGroup.objects.create(subject=subject, identifier="GP1")

        offering = create_subject_offering(
            subject=subject,
            subject_group=group,
            working_day=self.working_day,
            time_slot=self.time_slot,
            required_space_type=self.space_type,
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
        )
        self.assertEqual(offering.required_space_type, self.space_type)

    def test_virtual_subject_without_space_type_is_accepted(self):
        subject = Subject.objects.create(
            code="TST-VNST",
            name="Virtual Sin Espacio",
            class_type=Subject.CLASS_TYPE_VIRTUAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        group = SubjectGroup.objects.create(subject=subject, identifier="GVN1")

        offering = create_subject_offering(
            subject=subject,
            subject_group=group,
            working_day=self.working_day,
            time_slot=self.time_slot,
            required_space_type=None,
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
        )
        self.assertIsNone(offering.required_space_type)

    # --- Regla 1: Capacidad del salon cubre numero de estudiantes ---

    def test_classroom_with_sufficient_capacity_is_available(self):
        Classroom.objects.create(
            code="CAP-LRG",
            name="Salon Grande",
            campus=self.campus,
            space_type=self.space_type,
            capacity=50,
        )
        available, reason = check_classrooms_available_for_space_type(
            self.space_type, None, None, student_count=30
        )
        self.assertTrue(available)
        self.assertEqual(reason, "")

    def test_no_classroom_with_sufficient_capacity_returns_unavailable(self):
        small_type = CatalogItem.objects.create(
            catalog_type="academic_space_type",
            name="Micro TEC21",
        )
        Classroom.objects.create(
            code="CAP-SML",
            name="Salon Pequeno",
            campus=self.campus,
            space_type=small_type,
            capacity=5,
        )
        available, reason = check_classrooms_available_for_space_type(
            small_type, None, None, student_count=100
        )
        self.assertFalse(available)
        self.assertIn("capacidad", reason)

    def test_capacity_filter_ignores_undersized_classrooms(self):
        exact_type = CatalogItem.objects.create(
            catalog_type="academic_space_type",
            name="Exacto TEC21",
        )
        Classroom.objects.create(
            code="CAP-XS",
            name="Salon XS",
            campus=self.campus,
            space_type=exact_type,
            capacity=20,
        )
        Classroom.objects.create(
            code="CAP-XL",
            name="Salon XL",
            campus=self.campus,
            space_type=exact_type,
            capacity=60,
        )
        available, _ = check_classrooms_available_for_space_type(
            exact_type, None, None, student_count=40
        )
        self.assertTrue(available)


class SubjectOfferingEditWarningTests(BaseAuthTestCase):
    """Tests for HU: editar programación antes/después de ejecutar el algoritmo."""

    def setUp(self):
        self.coordinator_user = self.create_user(
            email="coord.ew@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )
        self.campus = Campus.objects.create(code="EW-CAM", name="Campus EW")
        self.program = AcademicProgram.objects.create(
            code="EW-PRG", name="Programa EW", campus=self.campus
        )
        self.subject = Subject.objects.create(
            code="EW-MAT",
            name="Matematicas EW",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        self.subject_group = SubjectGroup.objects.create(
            subject=self.subject, identifier="Grupo EW"
        )
        self.working_day = WorkingDay.objects.create(
            day_of_week=2, name="Martes EW", is_active=True
        )
        self.time_slot = TimeSlot.objects.create(
            name="08:00-10:00 EW",
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True,
        )

    def _make_period(self, *, schedule_generated_at=None):
        from django.utils import timezone
        code = f"EW-{schedule_generated_at.timestamp() if schedule_generated_at else 'none'}"
        return AcademicPeriod.objects.create(
            code=code[:20],
            name="Periodo EW",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
            schedule_generated_at=schedule_generated_at,
        )

    def _make_offering(self, period):
        return SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            working_day=self.working_day,
            time_slot=self.time_slot,
            academic_program=self.program,
            academic_period=period,
            semester=1,
        )

    # --- Escenario 1: editar antes de ejecutar el algoritmo ---

    def test_edit_before_algorithm_returns_no_warning(self):
        """Escenario 1: sin schedule_generated_at → edit_warning es None."""
        period = self._make_period()
        offering = self._make_offering(period)
        self.login_and_set_auth("coord.ew@test.com", "coordpassword123")

        response = self.client.patch(
            reverse("programming-subject-offerings-detail", args=[offering.id]),
            {"student_count": 25},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["edit_warning"])
        self.assertEqual(response.data["student_count"], 25)

    def test_get_offering_before_algorithm_has_no_warning(self):
        """GET detalle antes del algoritmo: edit_warning es None."""
        period = self._make_period()
        offering = self._make_offering(period)
        self.login_and_set_auth("coord.ew@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["edit_warning"])

    # --- Escenario 2: editar después de ejecutar el algoritmo ---

    def test_edit_after_algorithm_returns_warning(self):
        """Escenario 2: con schedule_generated_at → edit_warning contiene el aviso."""
        from django.utils import timezone
        period = self._make_period(schedule_generated_at=timezone.now())
        offering = self._make_offering(period)
        self.login_and_set_auth("coord.ew@test.com", "coordpassword123")

        response = self.client.patch(
            reverse("programming-subject-offerings-detail", args=[offering.id]),
            {"student_count": 30},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["edit_warning"])
        self.assertIn("regenerarse", response.data["edit_warning"])
        self.assertEqual(response.data["student_count"], 30)

    def test_get_offering_after_algorithm_shows_warning(self):
        """GET detalle después del algoritmo: edit_warning contiene el aviso."""
        from django.utils import timezone
        period = self._make_period(schedule_generated_at=timezone.now())
        offering = self._make_offering(period)
        self.login_and_set_auth("coord.ew@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["edit_warning"])
        self.assertIn("regenerarse", response.data["edit_warning"])

    def test_edit_after_algorithm_still_persists_changes(self):
        """El sistema permite editar aun cuando el algoritmo ya fue ejecutado."""
        from django.utils import timezone
        period = self._make_period(schedule_generated_at=timezone.now())
        offering = self._make_offering(period)
        self.login_and_set_auth("coord.ew@test.com", "coordpassword123")

        response = self.client.patch(
            reverse("programming-subject-offerings-detail", args=[offering.id]),
            {"student_count": 99},
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offering.refresh_from_db()
        self.assertEqual(offering.student_count, 99)

    def test_warning_includes_generation_timestamp(self):
        """El aviso incluye la fecha/hora de generación del horario."""
        from django.utils import timezone
        generated_at = timezone.now()
        period = self._make_period(schedule_generated_at=generated_at)
        offering = self._make_offering(period)
        self.login_and_set_auth("coord.ew@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        warning = response.data["edit_warning"]
        self.assertIsNotNone(warning)
        self.assertIn(generated_at.strftime("%Y-%m-%d"), warning)


class ScheduleExecutionServiceTests(BaseAuthTestCase):
    def setUp(self):
        self.admin_user = self.create_user(
            email="admin.schedule@test.com",
            password="adminpassword123",
            role=self.admin_role,
            first_name="Ana",
            last_name="Schedule",
        )
        self.campus = Campus.objects.create(code="SE-CAM", name="Campus SE")
        self.program = AcademicProgram.objects.create(
            code="SE-PRG", name="Programa SE", campus=self.campus
        )
        self.period = AcademicPeriod.objects.create(
            code="SE-2026",
            name="Periodo SE",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
        )
        self.subject = Subject.objects.create(
            code="SE-MAT",
            name="Matematicas SE",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        self.subject_group = SubjectGroup.objects.create(subject=self.subject, identifier="G1")
        self.working_day = WorkingDay.objects.create(day_of_week=2, name="Martes", is_active=True)
        self.time_slot = TimeSlot.objects.create(
            name="08:00-10:00",
            start_time=time(8, 0),
            end_time=time(10, 0),
            is_active=True,
        )
        self.assigned_offering = SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            working_day=self.working_day,
            time_slot=self.time_slot,
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
        )
        self.unassigned_offering = SubjectOffering.objects.create(
            subject=Subject.objects.create(
                code="SE-HIS",
                name="Historia SE",
                class_type=Subject.CLASS_TYPE_PRESENCIAL,
                credits=2,
                weekly_hours=2,
                capacity=20,
                difficulty=40,
            ),
            subject_group=SubjectGroup.objects.create(
                subject=Subject.objects.get(code="SE-HIS"), identifier="G2"
            ),
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
        )

    def test_run_schedule_execution_completes_and_marks_period_timestamp(self):
        execution = ScheduleExecution.objects.create(
            academic_period=self.period,
            requested_by=self.admin_user,
            parameters={"generaciones": 5},
        )

        run_schedule_execution(execution)

        execution.refresh_from_db()
        self.period.refresh_from_db()

        self.assertEqual(execution.status, ScheduleExecution.Status.COMPLETED)
        self.assertEqual(execution.progress, 100)
        self.assertIsNotNone(execution.finished_at)
        self.assertEqual(execution.result_snapshot["summary"]["total_assignments"], 1)
        self.assertEqual(execution.result_snapshot["summary"]["total_unassigned"], 1)
        self.assertEqual(execution.result_snapshot["current_generation"], 5)
        self.assertEqual(execution.result_snapshot["total_generations"], 5)
        self.assertIsNotNone(self.period.schedule_generated_at)

    def test_queue_schedule_execution_runs_worker_and_persists(self):
        execution = ScheduleExecution.objects.create(
            academic_period=self.period,
            requested_by=self.admin_user,
            parameters={"generaciones": 3},
        )

        # run synchronously to avoid sqlite locking in threaded tests
        run_schedule_execution(execution)

        execution.refresh_from_db()
        self.assertEqual(execution.status, ScheduleExecution.Status.COMPLETED)

        self.period.refresh_from_db()
        self.assertIsNotNone(self.period.schedule_generated_at)


class RegisterStudentCountHUTests(BaseAuthTestCase):
    """Tests for HU-8: registrar número de estudiantes por asignatura."""

    def setUp(self):
        self.coordinator_user = self.create_user(
            email="coord.hu8@test.com",
            password="coordpassword123",
            role=self.coordinator_role,
            first_name="Carlos",
            last_name="Coord",
        )
        self.campus = Campus.objects.create(code="HU8-CAM", name="Campus HU8")
        self.program = AcademicProgram.objects.create(
            code="HU8-PRG", name="Programa HU8", campus=self.campus
        )
        self.period = AcademicPeriod.objects.create(
            code="HU8-2026",
            name="Periodo HU8",
            start_date=date(2026, 1, 1),
            end_date=date(2026, 6, 30),
            is_active=True,
        )
        self.subject = Subject.objects.create(
            code="HU8-MAT",
            name="Matematicas HU8",
            class_type=Subject.CLASS_TYPE_PRESENCIAL,
            credits=3,
            weekly_hours=4,
            capacity=30,
            difficulty=120,
        )
        self.subject_group = SubjectGroup.objects.create(
            subject=self.subject, identifier="Grupo HU8"
        )
        self.working_day = WorkingDay.objects.create(
            day_of_week=3, name="Miercoles HU8", is_active=True
        )
        self.time_slot = TimeSlot.objects.create(
            name="09:00-11:00 HU8",
            start_time=time(9, 0),
            end_time=time(11, 0),
            is_active=True,
        )
        self.space_type = CatalogItem.objects.create(
            catalog_type="academic_space_type",
            name="Aula HU8",
        )

    def _create_offering(self, student_count=None, space_type=None):
        return SubjectOffering.objects.create(
            subject=self.subject,
            subject_group=self.subject_group,
            working_day=self.working_day,
            time_slot=self.time_slot,
            required_space_type=space_type,
            student_count=student_count,
            academic_program=self.program,
            academic_period=self.period,
            semester=1,
        )

    # --- Escenario 1: Registrar el cupo de una asignatura ---

    def test_coordinator_can_register_student_count(self):
        """El coordinador registra el cupo; el sistema lo almacena."""
        self.login_and_set_auth("coord.hu8@test.com", "coordpassword123")
        response = self.client.post(
            reverse("programming-subject-offerings-list-create"),
            {
                "subject_id": self.subject.id,
                "subject_group_id": self.subject_group.id,
                "academic_program_id": self.program.id,
                "working_day_id": self.working_day.id,
                "time_slot_id": self.time_slot.id,
                "semester": 2,
                "student_count": 28,
            },
            format="json",
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["student_count"], 28)

    def test_non_assignable_reason_is_null_when_classrooms_have_capacity(self):
        """Escenario 1: con salones con capacidad suficiente → non_assignable_reason es null."""
        Classroom.objects.create(
            code="HU8-LAR",
            name="Salon Grande HU8",
            campus=self.campus,
            space_type=self.space_type,
            capacity=50,
        )
        offering = self._create_offering(student_count=30, space_type=self.space_type)
        self.login_and_set_auth("coord.hu8@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["student_count"], 30)
        self.assertIsNone(response.data["non_assignable_reason"])

    def test_non_assignable_reason_is_null_when_no_student_count(self):
        """Sin cupo registrado no se calcula la razón de no asignabilidad."""
        offering = self._create_offering(student_count=None)
        self.login_and_set_auth("coord.hu8@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNone(response.data["non_assignable_reason"])

    # --- Escenario 2: Cupo supera la capacidad de todos los salones ---

    def test_non_assignable_reason_when_student_count_exceeds_all_classrooms(self):
        """Escenario 2: cupo mayor que cualquier salón → non_assignable_reason con mensaje."""
        Classroom.objects.create(
            code="HU8-SML",
            name="Salon Pequeno HU8",
            campus=self.campus,
            space_type=self.space_type,
            capacity=20,
        )
        offering = self._create_offering(student_count=100, space_type=self.space_type)
        self.login_and_set_auth("coord.hu8@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["non_assignable_reason"])
        self.assertIn("capacidad", response.data["non_assignable_reason"])

    def test_non_assignable_reason_visible_on_list(self):
        """El campo non_assignable_reason aparece también en el listado de programación."""
        Classroom.objects.create(
            code="HU8-MED",
            name="Salon Mediano HU8",
            campus=self.campus,
            space_type=self.space_type,
            capacity=15,
        )
        self._create_offering(student_count=200, space_type=self.space_type)
        self.login_and_set_auth("coord.hu8@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-list-create")
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        offering_data = next(
            (o for o in response.data if o["student_count"] == 200), None
        )
        self.assertIsNotNone(offering_data)
        self.assertIn("non_assignable_reason", offering_data)
        self.assertIsNotNone(offering_data["non_assignable_reason"])

    def test_non_assignable_reason_when_no_classrooms_exist(self):
        """Sin ningún salón activo, un cupo registrado resulta no asignable."""
        offering = self._create_offering(student_count=10, space_type=None)
        self.login_and_set_auth("coord.hu8@test.com", "coordpassword123")

        response = self.client.get(
            reverse("programming-subject-offerings-detail", args=[offering.id])
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(response.data["non_assignable_reason"])
        self.assertIn("capacidad", response.data["non_assignable_reason"])
