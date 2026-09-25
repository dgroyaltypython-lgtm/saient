from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied

from .models import Office, StaffProfile


def is_global_admin(user):
    # Only a Django superuser is a global office administrator.
    # A normal staff employee may have an assigned office, but must
    # never gain access to other offices merely because is_staff=True.
    return bool(
        user.is_authenticated and user.is_superuser
    )


def assigned_office(user):
    if not user.is_authenticated or is_global_admin(user):
        return None

    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return None

    if not profile.is_active or not profile.office.active:
        return None

    return profile.office


def require_staff_or_admin(user):
    if not user.is_authenticated:
        return redirect_to_login("/")

    if is_global_admin(user):
        return None

    if assigned_office(user) is None:
        raise PermissionDenied(
            "Your user account is not assigned to an active office."
        )

    return None


def get_allowed_office(user, office_id=None):
    if is_global_admin(user):
        if office_id is None:
            return None

        try:
            return Office.objects.get(pk=office_id, active=True)
        except Office.DoesNotExist:
            raise PermissionDenied("Office not found or inactive.")

    office = assigned_office(user)

    if office is None:
        raise PermissionDenied(
            "Your user account is not assigned to an active office."
        )

    if office_id is not None:
        try:
            requested_id = int(office_id)
        except (TypeError, ValueError):
            raise PermissionDenied("Invalid office.")

        if requested_id != office.id:
            raise PermissionDenied(
                "You are not allowed to access another office."
            )

    return office
