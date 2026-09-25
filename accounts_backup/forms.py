from decimal import Decimal
from django import forms
from .models import DailyEntry, Office


class DailyEntryForm(forms.ModelForm):
    class Meta:
        model = DailyEntry
        fields = [
            "office", "entry_date", "entry_type", "amount",
            "payment_mode", "reason", "reference", "notes",
        ]
        widgets = {
            "entry_date": forms.DateInput(attrs={"type": "date"}),
            "amount": forms.NumberInput(attrs={"min": "0.01", "step": "0.01"}),
            "reason": forms.TextInput(attrs={
                "placeholder": "Ticket collection / Diesel / Tea"
            }),
            "reference": forms.TextInput(attrs={
                "placeholder": "UTR / receipt / voucher no."
            }),
            "notes": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Optional notes"
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["office"].queryset = Office.objects.filter(active=True)
        self.fields["amount"].min_value = Decimal("0.01")

    def clean_reason(self):
        value = self.cleaned_data["reason"].strip()
        if not value:
            raise forms.ValidationError("Please enter a reason or description.")
        return value
