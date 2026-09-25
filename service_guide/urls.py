from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="service_guide"),
    path("clear/", views.clear_chat, name="service_guide_clear"),
]
