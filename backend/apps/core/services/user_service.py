from decimal import Decimal

from django.contrib.auth.models import User
from django.db import transaction

from apps.core.models import UserProfile, Teacher, CatalogItem


class UserServiceError(Exception):
    pass


class UserEmailAlreadyExistsError(UserServiceError):
    pass


def _email_exists(email, exclude_profile_id=None):
    profile_queryset = UserProfile.objects.filter(email__iexact=email)
    if exclude_profile_id is not None:
        profile_queryset = profile_queryset.exclude(id=exclude_profile_id)

    user_queryset = User.objects.filter(email__iexact=email)
    if exclude_profile_id is not None:
        user_queryset = user_queryset.exclude(profile__id=exclude_profile_id)

    return profile_queryset.exists() or user_queryset.exists()


def _username_exists(username, exclude_user_id=None):
    user_queryset = User.objects.filter(username__iexact=username)
    if exclude_user_id is not None:
        user_queryset = user_queryset.exclude(id=exclude_user_id)

    return user_queryset.exists()


@transaction.atomic
def create_user_with_profile(*, email, password, first_name, last_name, role):
    normalized_email = email.strip().lower()
    existing_user = User.objects.select_related("profile").filter(username__iexact=normalized_email).first()

    if existing_user and hasattr(existing_user, "profile"):
        raise UserEmailAlreadyExistsError("El correo ya existe en el sistema.")

    if _email_exists(normalized_email):
        raise UserEmailAlreadyExistsError("El correo ya existe en el sistema.")

    if existing_user:
        user = existing_user
        user.username = normalized_email
        user.email = normalized_email
        user.first_name = first_name
        user.last_name = last_name
        user.is_active = True
        user.set_password(password)
        user.save(update_fields=["username", "email", "first_name", "last_name", "is_active", "password"])
    else:
        user = User.objects.create_user(
            username=normalized_email,
            email=normalized_email,
            password=password,
            first_name=first_name,
            last_name=last_name,
            is_active=True,
        )

    profile = UserProfile.objects.create(
        user=user,
        role=role,
        first_name=first_name,
        last_name=last_name,
        email=normalized_email,
        is_active=True,
    )

    # If the created profile is a docente, create a corresponding Teacher record
    try:
        if role and getattr(role, "name", "").strip().lower() == "docente":
            # Find an active teacher link type to satisfy the non-null FK
            link_type = CatalogItem.objects.filter(
                catalog_type=CatalogItem.CatalogType.TEACHER_LINK_TYPE, is_active=True
            ).first()
            if link_type:
                Teacher.objects.create(
                    first_name=first_name,
                    last_name=last_name,
                    email=normalized_email,
                    user_profile=profile,
                    link_type=link_type,
                    hourly_rate=Decimal("1.00"),
                    is_active=True,
                )
    except Exception:
        # Do not break user creation if Teacher creation fails; log could be added
        pass

    return profile


@transaction.atomic
def update_user_profile(profile, *, email, first_name, last_name, role, is_active):
    normalized_email = email.strip().lower()
    if _email_exists(normalized_email, exclude_profile_id=profile.id):
        raise UserEmailAlreadyExistsError("El correo ya existe en el sistema.")

    if _username_exists(normalized_email, exclude_user_id=profile.user_id):
        raise UserEmailAlreadyExistsError("El correo ya existe en el sistema.")

    profile.email = normalized_email
    profile.first_name = first_name
    profile.last_name = last_name
    profile.role = role
    profile.is_active = is_active
    profile.save(
        update_fields=[
            "email",
            "first_name",
            "last_name",
            "role",
            "is_active",
            "updated_at",
        ]
    )

    user = profile.user
    user.username = normalized_email
    user.email = normalized_email
    user.first_name = first_name
    user.last_name = last_name
    user.is_active = is_active
    user.save(update_fields=["username", "email", "first_name", "last_name", "is_active"])

    return profile


@transaction.atomic
def deactivate_user_profile(profile):
    profile.is_active = False
    profile.save(update_fields=["is_active", "updated_at"])

    user = profile.user
    user.is_active = False
    user.save(update_fields=["is_active"])

    return profile
