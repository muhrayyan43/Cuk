from django.conf import settings


def site(request):
    """Membuat {{ SITE_NAME }} tersedia di semua template."""
    return {"SITE_NAME": settings.SITE_NAME}
