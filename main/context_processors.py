from urllib.parse import urlencode

from django.conf import settings
from django.urls import NoReverseMatch, reverse

from accounts.roles import CURATOR, GUEST, get_display_name, get_role

# (nama URL, label). Tautan baru muncul kalau nama URL-nya sudah ada, jadi menu
# terisi sendiri saat tiap modul dibuat. Ubah daftar ini untuk mengatur menu.
PUBLIC_ITEMS = [
    ("catalog:list", "Katalog"),
    ("shelves:list", "Shelf"),
]
MEMBER_ITEMS = [
    ("shelves:mine", "Shelf saya"),
    ("preferences:list", "Preferensi"),
    ("preferences:history", "Riwayat"),
    ("dataqueue:queue", "Antrean data"),
]


def site(request):
    """Membuat {{ SITE_NAME }} tersedia di semua template."""
    return {"SITE_NAME": settings.SITE_NAME}


def _reverse(name):
    try:
        return reverse(name)
    except NoReverseMatch:
        return None


def _mark_active(items, path):
    """Tandai satu item aktif: yang URL-nya paling panjang dan cocok dengan path."""
    best = None
    for item in items:
        url = item["url"]
        prefix = url if url.endswith("/") else url + "/"
        if path == url or path.startswith(prefix):
            if best is None or len(url) > len(best["url"]):
                best = item
    if best:
        best["active"] = True


def build_navigation(user, path, resolve=None):
    """Susun data navbar dan footer untuk satu pengguna.

    `resolve` (nama URL -> alamat atau None) bisa diganti, dipakai halaman rujukan
    komponen untuk mempratinjau tiga kondisi pengguna.
    """
    resolve = resolve or _reverse
    role = get_role(user)

    pairs = PUBLIC_ITEMS + ([] if role == GUEST else MEMBER_ITEMS)
    items = []
    for name, label in pairs:
        url = resolve(name)
        if url:
            items.append({"label": label, "url": url, "active": False})
    _mark_active(items, path)

    login_url = resolve("accounts:login")
    register_url = resolve("accounts:register")
    profile_url = resolve("accounts:profile")
    logout_url = resolve("accounts:logout")
    panel_url = resolve("kurator:dashboard") if role == CURATOR else None

    # Tautan Masuk membawa ?next=, kecuali di beranda dan halaman masuk/daftar.
    login_href = login_url
    if login_url and path.startswith("/") and path not in ("/", login_url, register_url):
        login_href = f"{login_url}?{urlencode({'next': path})}"

    if role == GUEST:
        links = [("Masuk", login_href), ("Daftar", register_url)]
    else:
        links = [("Profil", profile_url), ("Panel Kurator", panel_url)]

    return {
        "role": role,
        "items": items,
        "login_href": login_href,
        "register_url": register_url,
        "profile_url": profile_url,
        "logout_url": logout_url,
        "panel_url": panel_url,
        "display_name": get_display_name(user) if role != GUEST else "",
        "account_links": [{"label": label, "url": url} for label, url in links if url],
    }


def navigation(request):
    """Membuat {{ nav }} tersedia di semua template (navbar dan footer)."""
    return {"nav": build_navigation(getattr(request, "user", None), request.path)}