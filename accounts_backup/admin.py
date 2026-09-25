from django.contrib import admin
from .models import DailyEntry, Office


@admin.register(Office)
class OfficeAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "whatsapp", "active")
    list_filter = ("active",)
    search_fields = ("name", "phone", "whatsapp", "address")


@admin.register(DailyEntry)
class DailyEntryAdmin(admin.ModelAdmin):
    list_display = (
        "entry_date", "office", "entry_type", "payment_mode",
        "reason", "amount", "reference", "created_at",
    )
    list_filter = ("office", "entry_type", "payment_mode", "entry_date")
    search_fields = ("reason", "notes", "reference")
    date_hierarchy = "entry_date"
    ordering = ("-entry_date", "-created_at")


from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import StaffProfile

@admin.register(StaffProfile)
class StaffProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "office", "is_active", "created_at")
    list_filter = ("office", "is_active")
    search_fields = ("user__username", "user__first_name", "user__last_name", "office__name")
    autocomplete_fields = ("user", "office")
