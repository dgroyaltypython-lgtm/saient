from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from .models import StaffProfile, Office

def is_global_admin(user):
    return bool(user.is_authenticated and (user.is_superuser or user.is_staff))

def assigned_office(user):
    if not user.is_authenticated or is_global_admin(user):
        return None
    try:
        profile = user.staff_profile
    except StaffProfile.DoesNotExist:
        return None
    if not profile.is_active:
        return None
    return profile.office

def require_staff_or_admin(user):
    if not user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login("/")
    if is_global_admin(user):
        return None
    if assigned_office(user) is None:
        raise PermissionDenied("Your user account is not assigned to an active office.")
    return None

def get_allowed_office(user, office_id=None):
    if is_global_admin(user):
        if office_id is None:
            return None
        try:
            return Office.objects.get(pk=office_id)
        except Office.DoesNotExist:
            raise PermissionDenied("Office not found.")

    office = assigned_office(user)
    if office is None:
        raise PermissionDenied("Your user account is not assigned to an active office.")

    # Staff never get to choose another office through a URL/query parameter.
    if office_id is not None and int(office_id) != office.id:
        raise PermissionDenied("You are not allowed to access another office.")
    return office
