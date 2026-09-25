from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("entry/add/", views.add_entry, name="add_entry"),
    path("entry/<int:entry_id>/edit/", views.edit_entry, name="edit_entry"),
    path("entry/<int:entry_id>/delete/", views.delete_entry, name="delete_entry"),
    path("office/<int:office_id>/pdf/", views.daily_pdf, name="daily_pdf"),
    path("office/<int:office_id>/whatsapp/", views.whatsapp_daily, name="whatsapp_daily"),
    path("logout/", views.staff_logout, name="logout"),
]
