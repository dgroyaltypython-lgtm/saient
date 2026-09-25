from datetime import date
from decimal import Decimal
from urllib.parse import quote

from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from django.db.models import Q, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from .access import assigned_office, get_allowed_office, is_global_admin
from .models import DailyEntry, Office


def _selected_date(request):
    value = request.GET.get("date") or request.POST.get("date")
    if value:
        try:
            return date.fromisoformat(value)
        except ValueError:
            pass
    return date.today()


def _office_for_request(request, office_id=None):
    if is_global_admin(request.user):
        if office_id:
            return get_object_or_404(Office, pk=office_id)
        return Office.objects.filter(active=True).first()
    office = assigned_office(request.user)
    if office is None:
        return None
    if office_id and office.pk != int(office_id):
        from django.core.exceptions import PermissionDenied
        raise PermissionDenied("You cannot access another office.")
    return office


@login_required
@login_required
def dashboard(request):
    if not is_global_admin(request.user):
        office = get_allowed_office(request.user)
        offices = Office.objects.filter(pk=office.pk)
    else:
        offices = Office.objects.filter(active=True).order_by("name")
        office_id = request.GET.get("office")
        office = get_allowed_office(request.user, office_id) if office_id else offices.first()

    selected_date = parse_date(request.GET.get("date") or "") or timezone.localdate()
    entries = DailyEntry.objects.filter(office=office, entry_date=selected_date) if office else DailyEntry.objects.none()

    q = (request.GET.get("q") or "").strip()
    entry_type = (request.GET.get("type") or "").strip()
    payment_mode = (request.GET.get("payment") or "").strip()

    if q:
        from django.db.models import Q
        entries = entries.filter(Q(reason__icontains=q) | Q(notes__icontains=q) | Q(reference__icontains=q))
    if entry_type in ("expense", "collection"):
        entries = entries.filter(entry_type=entry_type)
    if payment_mode in ("cash", "upi"):
        entries = entries.filter(payment_mode=payment_mode)

    total_expense = entries.filter(entry_type="expense").aggregate(total=Sum("amount"))["total"] or 0
    total_collection = entries.filter(entry_type="collection").aggregate(total=Sum("amount"))["total"] or 0
    context = {
        "offices": offices,
        "selected_office": office,
        "selected_date": selected_date,
        "entries": entries,
        "total_expense": total_expense,
        "total_collection": total_collection,
        "net": total_collection - total_expense,
        "entry_count": entries.count(),
        "is_admin": is_global_admin(request.user),
        "q": q,
        "selected_type": entry_type,
        "selected_payment": payment_mode,
    }
    return render(request, "accounts/dashboard.html", context)

def add_entry(request):
    office = _office_for_request(request, request.POST.get("office") if is_global_admin(request.user) and request.method == "POST" else None)
    offices = Office.objects.filter(active=True).order_by("name") if is_global_admin(request.user) else Office.objects.filter(pk=getattr(assigned_office(request.user), "pk", None))

    if request.method == "POST":
        if not office:
            messages.error(request, "No active office is assigned to this account.")
            return redirect("dashboard")

        entry = DailyEntry(
            office=office,
            entry_date=request.POST.get("date") or date.today(),
            entry_type=request.POST.get("entry_type", "collection"),
            amount=request.POST.get("amount") or 0,
            payment_mode=request.POST.get("payment_mode", "cash"),
            reason=request.POST.get("reason", "").strip(),
            notes=request.POST.get("notes", "").strip(),
            reference=request.POST.get("reference", "").strip(),
        )
        entry.full_clean()
        entry.save()
        messages.success(request, "Entry saved successfully.")
        return redirect(f"{reverse('dashboard')}?office={office.pk}&date={entry.entry_date}")

    return render(request, "accounts/add_entry.html", {
        "offices": offices,
        "selected_office": office,
        "today": date.today(),
        "is_global_admin": is_global_admin(request.user),
    })


@login_required
def edit_entry(request, entry_id):
    entry = get_object_or_404(DailyEntry, pk=entry_id)
    get_allowed_office(request.user, entry.office_id)
    office = get_allowed_office(request.user, entry.office_id)

    if request.method == "POST":
        entry.entry_date = request.POST.get("date") or entry.entry_date
        entry.entry_type = request.POST.get("entry_type", entry.entry_type)
        entry.amount = request.POST.get("amount") or entry.amount
        entry.payment_mode = request.POST.get("payment_mode", entry.payment_mode)
        entry.reason = request.POST.get("reason", "").strip()
        entry.notes = request.POST.get("notes", "").strip()
        entry.reference = request.POST.get("reference", "").strip()
        entry.full_clean()
        entry.save()
        messages.success(request, "Entry updated successfully.")
        return redirect(f"{reverse('dashboard')}?office={office.pk}&date={entry.entry_date}")

    return render(request, "accounts/edit_entry.html", {
        "entry": entry,
        "office": office,
        "is_global_admin": is_global_admin(request.user),
    })


@login_required
def delete_entry(request, entry_id):
    entry = get_object_or_404(DailyEntry, pk=entry_id)
    get_allowed_office(request.user, entry.office_id)
    office = get_allowed_office(request.user, entry.office_id)

    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted successfully.")
    return redirect(f"{reverse('dashboard')}?office={office.pk}&date={entry.entry_date}")


@login_required
def daily_pdf(request, office_id):
    office = get_allowed_office(request.user, office_id)
    selected_date = _selected_date(request)
    entries = DailyEntry.objects.filter(office=office, entry_date=selected_date).order_by("created_at")

    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        return HttpResponse("ReportLab is not installed.", status=500)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="daily_{office.pk}_{selected_date}.pdf"'
    pdf = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(40, height - 50, "Saiprasad Tours and Travels")
    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 70, f"Office: {office.name}")
    pdf.drawString(40, height - 86, f"Date: {selected_date}")

    y = height - 120
    collection = Decimal("0")
    expense = Decimal("0")

    pdf.setFont("Helvetica-Bold", 9)
    pdf.drawString(40, y, "Type")
    pdf.drawString(100, y, "Reason")
    pdf.drawString(320, y, "Mode")
    pdf.drawString(400, y, "Reference")
    pdf.drawRightString(550, y, "Amount")
    y -= 18
    pdf.setFont("Helvetica", 8)

    for e in entries:
        if y < 50:
            pdf.showPage()
            y = height - 50
        pdf.drawString(40, y, e.get_entry_type_display())
        pdf.drawString(100, y, (e.reason or "")[:35])
        pdf.drawString(320, y, e.get_payment_mode_display())
        pdf.drawString(400, y, (e.reference or "")[:20])
        pdf.drawRightString(550, y, f"Rs. {e.amount:.2f}")
        if e.entry_type == "collection":
            collection += e.amount
        else:
            expense += e.amount
        y -= 15

    y -= 10
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, f"Collection: Rs. {collection:.2f}")
    pdf.drawString(220, y, f"Expenses: Rs. {expense:.2f}")
    pdf.drawString(400, y, f"Net: Rs. {(collection-expense):.2f}")
    pdf.save()
    return response


@login_required
def whatsapp_daily(request, office_id):
    office = get_allowed_office(request.user, office_id)
    selected_date = _selected_date(request)
    entries = DailyEntry.objects.filter(office=office, entry_date=selected_date)
    collection = entries.filter(entry_type="collection").aggregate(total=Sum("amount"))["total"] or Decimal("0")
    expense = entries.filter(entry_type="expense").aggregate(total=Sum("amount"))["total"] or Decimal("0")
    text = (
        f"Saiprasad Tours and Travels\n"
        f"Office: {office.name}\n"
        f"Date: {selected_date}\n"
        f"Collection: Rs. {collection:.2f}\n"
        f"Expenses: Rs. {expense:.2f}\n"
        f"Net Balance: Rs. {(collection-expense):.2f}"
    )
    return redirect("https://wa.me/?text=" + quote(text))


def staff_logout(request):
    logout(request)
    return redirect("login")
