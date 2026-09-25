from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.views import LoginView as _LoginView
from django.shortcuts import redirect, render
from django.urls import NoReverseMatch, reverse
from django.views.decorators.http import require_POST

from accounts.roles import is_curator

from .forms import LoginForm, RegisterForm


def register(request):
    """Daftar akun baru. Pengguna yang sudah login dikirim ke beranda."""
    if request.user.is_authenticated:
        return redirect("main:landing")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            auth_login(request, user)
            messages.success(request, f"Selamat datang, {user.profile.display_name}! Akunmu berhasil dibuat.")
            return redirect("main:landing")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


class LoginView(_LoginView):
    """Login bawaan Django. Redirect setelah masuk mengikuti `next`, atau role."""

    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Selamat datang kembali, {self.request.user.profile.display_name}.")
        return response

    def get_success_url(self):
        url = self.get_redirect_url()
        if url:
            return url
        if is_curator(self.request.user):
            try:
                return reverse("kurator:dashboard")
            except NoReverseMatch:
                pass  # panel Kurator belum dibuat (dibuat di langkah 12)
        return reverse("main:landing")


@require_POST
def logout(request):
    """Logout hanya lewat POST (navbar mengirim form, bukan tautan biasa)."""
    auth_logout(request)
    messages.info(request, "Kamu sudah keluar.")
    return redirect("main:landing")