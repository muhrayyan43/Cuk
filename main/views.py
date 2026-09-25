from types import SimpleNamespace

from django import forms
from django.conf import settings
from django.http import Http404
from django.shortcuts import render

from .context_processors import build_navigation
from .templatetags.ui import ICONS


def landing(request):
    """Sementara: kerangka. Landing page sebenarnya dibuat di Bagian C."""
    return render(request, "main/landing.html", {"show_styleguide": settings.DEBUG})


class _DemoForm(forms.Form):
    """Form contoh untuk halaman rujukan komponen (tidak dipakai di tempat lain)."""

    display_name = forms.CharField(
        label="Nama tampilan", max_length=60, help_text="Nama ini tampil di shelf publikmu."
    )
    email = forms.EmailField(label="Email", required=False)
    category = forms.ChoiceField(
        label="Kategori",
        choices=[("", "Pilih kategori"), ("mie", "Mie instan"), ("susu", "Susu dan pengganti")],
    )
    note = forms.CharField(label="Catatan", required=False, widget=forms.Textarea(attrs={"rows": 3}))


def styleguide(request):
    """Halaman rujukan komponen. Hanya aktif saat DEBUG; dinonaktifkan di server."""
    if not settings.DEBUG:
        raise Http404
    form = _DemoForm(data={"display_name": "", "email": "budi@", "category": "mie"})
    context = {"form": form, "icon_names": sorted(ICONS)}
    context.update(_demo_navs())
    return render(request, "main/styleguide.html", context)


def _demo_navs():
    """Navbar/footer untuk tiga kondisi pengguna, memakai kode navigasi yang sama
    dengan situs. Semua tautan dibuat palsu ("#nama") supaya semua menu tampil."""
    def fake_user(role):
        profile = SimpleNamespace(role=role, display_name="Rayyan")
        return SimpleNamespace(is_authenticated=True, profile=profile, get_username=lambda: "rayyan")

    resolve = lambda name: "#" + name  # noqa: E731
    path = "#catalog:list"
    return {
        "nav_guest": build_navigation(None, path, resolve),
        "nav_user": build_navigation(fake_user("user"), path, resolve),
        "nav_curator": build_navigation(fake_user("curator"), path, resolve),
    }