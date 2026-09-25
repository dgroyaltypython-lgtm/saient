from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import GroupAdmin, UserAdmin
from django.contrib.auth.models import Group

from .models import DailyEntry, Office, StaffProfile


class SuperuserOnlyAdminSite(admin.AdminSite):
    site_header = "Sai Enterprises Administration"
    site_title = "Sai Enterprises Admin"
    index_title = "Sai Enterprises Administration"

    def has_permission(self, request):
        # Only superusers may enter Django Admin.
        # Normal office employees use the application dashboard instead.
        return bool(
            request.user.is_active and request.user.is_superuser
        )


site = SuperuserOnlyAdminSite(name="sai_admin")


class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "whatsapp", "active")
    list_filter = ("active",)
    search_fields = ("name", "phone", "whatsapp", "address")


class DailyEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_date",
        "office",
        "entry_type",
        "payment_mode",
        "reason",
        "amount",
        "reference",
        "created_at",
    )
    list_filter = ("office", "entry_type", "payment_mode", "entry_date")
    search_fields = ("reason", "notes", "reference")
    date_hierarchy = "entry_date"
    ordering = ("-entry_date", "-created_at")


class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "office", "is_active", "created_at")
    list_filter = ("office", "is_active")
    search_fields = (
        "user__username",
        "user__first_name",
        "user__last_name",
        "office__name",
    )


# Django authentication models are registered on this custom admin site so
# the global superuser can create/manage employee login accounts and groups.
User = get_user_model()
site.register(User, UserAdmin)
site.register(Group, GroupAdmin)

site.register(Office, OfficeAdmin)
site.register(DailyEntry, DailyEntryAdmin)
site.register(StaffProfile, StaffProfileAdmin)
