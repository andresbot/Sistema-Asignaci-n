from rest_framework.permissions import BasePermission


def normalize_role_name(value):
    return (value or "").strip().lower()


def get_user_role_name(user):
    if not user or not user.is_authenticated:
        return None

    if getattr(user, "is_superuser", False):
        return "administrador"

    profile = getattr(user, "profile", None)
    if profile and profile.role_id:
        return normalize_role_name(profile.role.name)

    return None


class HasAllowedRoles(BasePermission):
    message = "No tiene permisos para acceder a este recurso."

    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        allowed_roles = getattr(view, "allowed_roles", ())
        if not allowed_roles:
            return True

        user_role_name = normalize_role_name(get_user_role_name(request.user))
        allowed_role_names = {
            normalize_role_name(role_name) for role_name in allowed_roles
        }

        return user_role_name in allowed_role_names
