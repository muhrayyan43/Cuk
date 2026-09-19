from django.conf import settings
from django.contrib import admin
from django.urls import include, path

# Django admin hanya untuk superuser darurat. Role Kurator (di Profile)
# bukan superuser, jadi Kurator memakai panel kustom, bukan admin ini.
admin.site.has_permission = lambda request: (
    request.user.is_active and request.user.is_superuser
)
admin.site.site_header = f"{settings.SITE_NAME}: Admin Darurat"

urlpatterns = [
    path(settings.ADMIN_URL, admin.site.urls),
    path("", include("main.urls")),
]