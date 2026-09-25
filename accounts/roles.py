"""Peran pengguna. Dipakai navbar/footer sekarang, dan decorator akses di Bagian B."""
from django.core.exceptions import ObjectDoesNotExist

from .models import Profile

GUEST = "guest"
USER = Profile.Role.USER      # "user"
CURATOR = Profile.Role.CURATOR  # "curator"


def get_role(user):
    """Kembalikan 'guest', 'user', atau 'curator'.

    Sumber kebenarannya Profile.role, bukan is_staff/is_superuser: superuser
    Django tidak otomatis menjadi Kurator.
    """
    if user is None or not getattr(user, "is_authenticated", False):
        return GUEST
    try:
        profile = user.profile
    except ObjectDoesNotExist:  # akun lama tanpa Profile dianggap pengguna biasa
        return USER
    return CURATOR if profile.role == Profile.Role.CURATOR else USER


def is_curator(user):
    return get_role(user) == CURATOR


def get_display_name(user):
    try:
        name = user.profile.display_name
    except ObjectDoesNotExist:
        name = ""
    return name or user.get_username()