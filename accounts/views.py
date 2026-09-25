from decimal import Decimal
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.utils.dateparse import parse_date

from .access import assigned_office, get_allowed_office, is_global_admin
from .forms import DailyEntryForm
from .models import DailyEntry, Office


def _selected_date(request):
    value = request.GET.get("date") or request.POST.get("date")
    parsed = parse_date(value or "")
    return parsed or timezone.localdate()


def _office_for_request(request, office_id=None):
    if is_global_admin(request.user):
        if office_id:
            return get_allowed_office(request.user, office_id)
        return Office.objects.filter(active=True).order_by("name").first()

    return get_allowed_office(request.user)


@login_required
def dashboard(request):
    global_admin = is_global_admin(request.user)

    if global_admin:
        offices = Office.objects.filter(active=True).order_by("name")
        office_id = request.GET.get("office")
        if office_id:
            office = get_allowed_office(request.user, office_id)
        else:
            office = offices.first()
    else:
        office = assigned_office(request.user)
        # Staff never receive an office list/dropdown. Their assigned office
        # is resolved server-side and is the only office they can access.
        offices = Office.objects.none()

    selected_date = _selected_date(request)

    entries = DailyEntry.objects.none()
    if office:
        entries = DailyEntry.objects.filter(
            office=office,
            entry_date=selected_date,
        )

    q = (request.GET.get("q") or "").strip()
    entry_type = (request.GET.get("type") or "").strip()
    payment_mode = (request.GET.get("payment") or "").strip()

    if q:
        entries = entries.filter(
            Q(reason__icontains=q) |
            Q(notes__icontains=q) |
            Q(reference__icontains=q)
        )

    if entry_type in ("collection", "expense"):
        entries = entries.filter(entry_type=entry_type)

    if payment_mode in ("cash", "upi"):
        entries = entries.filter(payment_mode=payment_mode)

    entries = entries.order_by("-created_at")

    collection = (
        entries.filter(entry_type="collection")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )
    expense = (
        entries.filter(entry_type="expense")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )
    cash_collection = (
        entries.filter(
            entry_type="collection",
            payment_mode="cash",
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )
    upi_collection = (
        entries.filter(
            entry_type="collection",
            payment_mode="upi",
        ).aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    context = {
        "offices": offices,
        "selected_office": office,
        "selected_date": selected_date,
        "entries": entries,
        "collection": collection,
        "cash_collection": cash_collection,
        "upi_collection": upi_collection,
        "expense": expense,
        "balance": collection - expense,
        "entry_count": entries.count(),
        "is_global_admin": global_admin,
        "staff_office": None if global_admin else office,
        "q": q,
        "selected_type": entry_type,
        "selected_payment": payment_mode,
    }

    return render(request, "accounts/dashboard.html", context)


@login_required
def add_entry(request):
    global_admin = is_global_admin(request.user)
    staff_office = assigned_office(request.user)

    if not global_admin and staff_office is None:
        return render(
            request,
            "accounts/dashboard.html",
            {
                "offices": Office.objects.none(),
                "selected_office": None,
                "selected_date": timezone.localdate(),
                "entries": DailyEntry.objects.none(),
                "is_global_admin": False,
                "staff_office": None,
            },
        )

    if request.method == "POST":
        if global_admin:
            office_id = request.POST.get("office")
            office = get_allowed_office(request.user, office_id)
        else:
            office = staff_office

        form = DailyEntryForm(request.POST)

        if not global_admin:
            form.fields["office"].queryset = Office.objects.filter(
                pk=office.pk
            )
            form.fields["office"].initial = office
            form.fields["office"].disabled = True

        if form.is_valid():
            entry = form.save(commit=False)
            entry.office = office
            entry.save()

            messages.success(request, "Entry saved successfully.")

            return redirect(
                f"{reverse('dashboard')}?office={office.pk}"
                f"&date={entry.entry_date.isoformat()}"
            )
    else:
        initial = {"entry_date": timezone.localdate()}
        if staff_office:
            initial["office"] = staff_office

        form = DailyEntryForm(initial=initial)

        if not global_admin and staff_office:
            form.fields["office"].queryset = Office.objects.filter(
                pk=staff_office.pk
            )
            form.fields["office"].disabled = True

    return render(
        request,
        "accounts/add_entry.html",
        {
            "form": form,
            "page_title": "Edit Entry" if False else "Daily Entry",
            "editing": False,
            "entry": None,
            "is_global_admin": global_admin,
            "staff_office": staff_office,
        },
    )


@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(DailyEntry, pk=entry_id)
    office = get_allowed_office(request.user, entry.office_id)

    if request.method == "POST":
        form = DailyEntryForm(request.POST, instance=entry)
        form.fields.pop("office", None)

        if form.is_valid():
            updated = form.save(commit=False)
            updated.office = office
            updated.save()

            messages.success(request, "Entry updated successfully.")

            return redirect(
                f"{reverse('dashboard')}?office={office.pk}"
                f"&date={updated.entry_date.isoformat()}"
            )
    else:
        form = DailyEntryForm(instance=entry)
        form.fields.pop("office", None)

    return render(
        request,
        "accounts/add_entry.html",
        {
            "form": form,
            "page_title": "Edit Entry",
            "editing": True,
            "entry": entry,
            "is_global_admin": is_global_admin(request.user),
            "staff_office": assigned_office(request.user),
        },
    )


@login_required
def delete_entry(request, entry_id):
    if request.method != "POST":
        raise PermissionDenied("Delete requests must use POST.")

    entry = get_object_or_404(DailyEntry, pk=entry_id)
    office = get_allowed_office(request.user, entry.office_id)
    entry_date = entry.entry_date

    entry.delete()

    messages.success(request, "Entry deleted successfully.")

    return redirect(
        f"{reverse('dashboard')}?office={office.pk}"
        f"&date={entry_date.isoformat()}"
    )


@login_required
def daily_pdf(request, office_id):
    office = get_allowed_office(request.user, office_id)
    selected_date = _selected_date(request)

    entries = DailyEntry.objects.filter(
        office=office,
        entry_date=selected_date,
    ).order_by("created_at")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return HttpResponse(
            "ReportLab is not installed.",
            status=500,
        )

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="sai_enterprises_daily_'
        f'{office.pk}_{selected_date}.pdf"'
    )

    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 50, "Sai Enterprises")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 70, f"Office: {office.name}")
    pdf.drawString(40, height - 86, f"Date: {selected_date}")

    y = height - 120
    collection = Decimal("0.00")
    expense = Decimal("0.00")

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, "Type")
    pdf.drawString(100, y, "Reason")
    pdf.drawString(320, y, "Mode")
    pdf.drawString(400, y, "Reference")
    pdf.drawRightString(550, y, "Amount")

    y -= 18
    pdf.setFont("Helvetica", 8)

    for entry in entries:
        if y < 55:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 8)

        pdf.drawString(40, y, entry.get_entry_type_display())
        pdf.drawString(100, y, (entry.reason or "")[:35])
        pdf.drawString(320, y, entry.get_payment_mode_display())
        pdf.drawString(400, y, (entry.reference or "")[:20])
        pdf.drawRightString(550, y, f"Rs. {entry.amount:.2f}")

        if entry.entry_type == "collection":
            collection += entry.amount
        else:
            expense += entry.amount

        y -= 15

    y -= 10
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, f"Collection: Rs. {collection:.2f}")
    pdf.drawString(220, y, f"Expenses: Rs. {expense:.2f}")
    pdf.drawString(400, y, f"Net: Rs. {(collection - expense):.2f}")

    pdf.save()

    return response


@login_required
def whatsapp_daily(request, office_id):
    office = get_allowed_office(request.user, office_id)
    selected_date = _selected_date(request)

    entries = DailyEntry.objects.filter(
        office=office,
        entry_date=selected_date,
    )

    collection = (
        entries.filter(entry_type="collection")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )
    expense = (
        entries.filter(entry_type="expense")
        .aggregate(total=Sum("amount"))["total"]
        or Decimal("0.00")
    )

    text = (
        f"Sai Enterprises\n"
        f"Office: {office.name}\n"
        f"Date: {selected_date}\n"
        f"Collection: Rs. {collection:.2f}\n"
        f"Expenses: Rs. {expense:.2f}\n"
        f"Net Balance: Rs. {(collection - expense):.2f}"
    )

    return redirect("https://wa.me/?text=" + quote(text))


@login_required
def staff_logout(request):
    logout(request)
    return redirect("login")
