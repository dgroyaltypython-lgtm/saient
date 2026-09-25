from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from accounts.admin import site as sai_admin_site

urlpatterns = [
    path("admin/", sai_admin_site.urls),
    path("login/", auth_views.LoginView.as_view(
        template_name="accounts/login.html"
    ), name="login"),
    path("", include("accounts.urls")),
]
