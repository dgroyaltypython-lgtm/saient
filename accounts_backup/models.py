from django.conf import settings
from django.db import models


class Office(models.Model):
    name = models.CharField(max_length=120)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    whatsapp = models.CharField(max_length=30, blank=True)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class DailyEntry(models.Model):
    ENTRY_TYPES = [
        ("collection", "Collection"),
        ("expense", "Expense"),
    ]
    PAYMENT_MODES = [
        ("cash", "Cash"),
        ("upi", "UPI"),
    ]

    office = models.ForeignKey(
        Office, on_delete=models.CASCADE, related_name="entries"
    )
    entry_date = models.DateField()
    entry_type = models.CharField(max_length=20, choices=ENTRY_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_mode = models.CharField(max_length=10, choices=PAYMENT_MODES)
    reason = models.CharField(max_length=255)
    notes = models.TextField(blank=True)
    reference = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-entry_date", "-created_at"]
        indexes = [
            models.Index(fields=["office", "entry_date"], name="dailyentry_office_date_idx"),
            models.Index(fields=["entry_type", "entry_date"], name="dailyentry_type_date_idx"),
        ]
    def __str__(self):
        return f"{self.office.name} - {self.entry_type} - ₹{self.amount:,.2f}"


class StaffProfile(models.Model):
    """Links a Django user to exactly one office."""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="staff_profile",
    )
    office = models.ForeignKey(
        Office,
        on_delete=models.PROTECT,
        related_name="staff_members",
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.office.name}"
