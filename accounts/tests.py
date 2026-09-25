from django.contrib.auth.models import User
from django.test import TestCase

from .forms import LoginForm, RegisterForm
from .roles import get_role, is_curator


def make_user(username, role="user", **extra):
    user = User.objects.create_user(username, password="Rahasia12345", **extra)
    user.profile.role = role
    user.profile.display_name = username.capitalize()
    user.profile.save()
    return user


VALID_DATA = {
    "username": "budi123",
    "email": "budi@contoh.com",
    "display_name": "Budi Santoso",
    "password1": "KataSandiKuat9",
    "password2": "KataSandiKuat9",
}


class RegisterFormTests(TestCase):
    def test_valid_data_creates_user_and_profile(self):
        form = RegisterForm(data=VALID_DATA)
        self.assertTrue(form.is_valid(), form.errors)
        user = form.save()
        self.assertEqual(user.email, "budi@contoh.com")
        self.assertEqual(user.profile.display_name, "Budi Santoso")
        self.assertEqual(user.profile.role, "user")  # peran default, bukan curator

    def test_email_is_stored_lowercase(self):
        data = {**VALID_DATA, "email": "Budi@Contoh.COM"}
        form = RegisterForm(data=data)
        self.assertTrue(form.is_valid(), form.errors)
        self.assertEqual(form.save().email, "budi@contoh.com")

    def test_duplicate_email_is_rejected_case_insensitively(self):
        make_user("lain", email="budi@contoh.com")
        form = RegisterForm(data={**VALID_DATA, "username": "budi456", "email": "BUDI@contoh.com"})
        self.assertFalse(form.is_valid())
        self.assertIn("email", form.errors)

    def test_password_mismatch_is_rejected(self):
        form = RegisterForm(data={**VALID_DATA, "password2": "bedasekali123"})
        self.assertFalse(form.is_valid())
        self.assertIn("password2", form.errors)

    def test_common_password_is_rejected(self):
        form = RegisterForm(data={**VALID_DATA, "password1": "password123", "password2": "password123"})
        self.assertFalse(form.is_valid())

    def test_display_name_is_required(self):
        form = RegisterForm(data={**VALID_DATA, "display_name": ""})
        self.assertFalse(form.is_valid())
        self.assertIn("display_name", form.errors)

    def test_labels_use_consistent_terms(self):
        form = RegisterForm()
        self.assertEqual(form.fields["password1"].label, "Kata sandi")
        self.assertEqual(form.fields["password2"].label, "Konfirmasi kata sandi")


class LoginFormTests(TestCase):
    def test_friendly_error_on_wrong_password(self):
        make_user("budi")
        form = LoginForm(data={"username": "budi", "password": "salah"})
        self.assertFalse(form.is_valid())
        self.assertIn("Username atau kata sandi salah", str(form.errors))


class AuthFlowTests(TestCase):
    def test_register_page_renders(self):
        response = self.client.get("/accounts/daftar/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Buat akun")

    def test_register_success_logs_in_and_redirects_home(self):
        response = self.client.post("/accounts/daftar/", VALID_DATA, follow=True)
        self.assertRedirects(response, "/")
        self.assertTrue(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Akunmu berhasil dibuat")

    def test_register_failure_shows_form_again_without_saving(self):
        response = self.client.post("/accounts/daftar/", {**VALID_DATA, "password2": "beda-semua-1"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="budi123").exists())

    def test_authenticated_user_is_redirected_away_from_register_and_login(self):
        self.client.force_login(make_user("budi"))
        self.assertEqual(self.client.get("/accounts/daftar/").status_code, 302)
        self.assertEqual(self.client.get("/accounts/masuk/").status_code, 302)

    def test_login_redirects_to_next(self):
        make_user("budi")
        response = self.client.post(
            "/accounts/masuk/?next=/shelves/saya/", {"username": "budi", "password": "Rahasia12345"}
        )
        self.assertRedirects(response, "/shelves/saya/", fetch_redirect_response=False)

    def test_login_without_next_goes_home_for_regular_user(self):
        make_user("budi")
        response = self.client.post("/accounts/masuk/", {"username": "budi", "password": "Rahasia12345"})
        self.assertRedirects(response, "/")

    def test_login_without_next_falls_back_to_home_when_curator_panel_is_missing(self):
        """Panel Kurator belum dibuat (langkah 12): redirect tidak boleh error."""
        make_user("sari", role="curator")
        response = self.client.post("/accounts/masuk/", {"username": "sari", "password": "Rahasia12345"})
        self.assertRedirects(response, "/")

    def test_login_shows_friendly_message_on_failure(self):
        make_user("budi")
        response = self.client.post("/accounts/masuk/", {"username": "budi", "password": "salah"})
        self.assertContains(response, "Username atau kata sandi salah")

    def test_logout_requires_post(self):
        self.client.force_login(make_user("budi"))
        self.assertEqual(self.client.get("/accounts/keluar/").status_code, 405)

    def test_logout_via_post_ends_session(self):
        self.client.force_login(make_user("budi"))
        response = self.client.post("/accounts/keluar/", follow=True)
        self.assertFalse(response.wsgi_request.user.is_authenticated)
        self.assertContains(response, "Kamu sudah keluar")

    def test_navbar_shows_display_name_not_username(self):
        make_user("budi99", role="user")
        self.client.login(username="budi99", password="Rahasia12345")
        response = self.client.get("/")
        self.assertContains(response, "Budi99")


class RoleHelperTests(TestCase):
    """Duplikat ringan dari main.tests.RoleTests, ditinjau dari sisi accounts."""

    def test_default_role_is_user(self):
        self.assertEqual(get_role(make_user("budi")), "user")

    def test_curator_role(self):
        self.assertTrue(is_curator(make_user("sari", role="curator")))