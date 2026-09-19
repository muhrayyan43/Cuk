from django import forms
from django.conf import settings
from django.http import Http404
from django.shortcuts import render

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
    return render(request, "main/styleguide.html", {"form": form, "icon_names": sorted(ICONS)})
