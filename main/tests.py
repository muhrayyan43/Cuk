from django import forms
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.contrib.messages import constants
from django.contrib.messages.storage.base import Message
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import Client, RequestFactory, SimpleTestCase, TestCase, override_settings
from django.urls import reverse
from django.views.defaults import permission_denied, server_error

from .templatetags.ui import ICONS, normalize_score


def render(template_string, **context):
    return Template("{% load ui %}" + template_string).render(Context(context))


class NormalizeScoreTests(SimpleTestCase):
    def test_valid_grades(self):
        self.assertEqual(normalize_score("nutri", "a"), ("ok", "a"))
        self.assertEqual(normalize_score("nutri", "E"), ("ok", "e"))
        self.assertEqual(normalize_score("green", " c "), ("ok", "c"))
        self.assertEqual(normalize_score("nova", 4), ("ok", "4"))

    def test_unknown_values_are_normalized(self):
        for value in (None, "", "unknown", "UNKNOWN", "f", "z", 9, "ab"):
            with self.subTest(value=value):
                self.assertEqual(normalize_score("nutri", value), ("unknown", ""))

    def test_not_applicable(self):
        for value in ("not-applicable", "NOT-APPLICABLE", "not_applicable"):
            with self.subTest(value=value):
                self.assertEqual(normalize_score("green", value), ("na", ""))

    def test_grade_sets_are_per_kind(self):
        self.assertEqual(normalize_score("nova", 5)[0], "unknown")
        self.assertEqual(normalize_score("nova", "a")[0], "unknown")
        self.assertEqual(normalize_score("nutri", 1)[0], "unknown")

    def test_unknown_kind_raises(self):
        with self.assertRaises(ValueError):
            normalize_score("eco", "a")


class ScoreBadgeRenderTests(SimpleTestCase):
    def test_ok_badge(self):
        html = render('{% score_badge "nutri" "b" %}')
        self.assertIn('data-grade="b"', html)
        self.assertIn('aria-label="Nutri-Score B"', html)
        self.assertIn(">B</span>", html)
        self.assertNotIn("is-estimate", html)

    def test_estimate_is_marked_differently(self):
        html = render('{% score_badge "green" "c" estimate=True label=True %}')
        self.assertIn("is-estimate", html)
        self.assertIn("(estimasi)", html)
        self.assertIn("Estimasi", html)

    def test_unknown_cannot_be_an_estimate(self):
        html = render('{% score_badge "green" "unknown" estimate=True label=True %}')
        self.assertNotIn("is-estimate", html)
        self.assertIn("score--unknown", html)
        self.assertIn("Tidak diketahui", html)

    def test_raw_api_words_never_shown(self):
        html = render('{% score_badge "nutri" "unknown" %}{% score_badge "nutri" "not-applicable" %}')
        self.assertNotIn(">unknown<", html)
        self.assertNotIn("not-applicable</", html)
        self.assertIn("score--na", html)


class IconTagTests(SimpleTestCase):
    def test_decorative_by_default(self):
        html = render('{% icon "check" %}')
        self.assertIn('aria-hidden="true"', html)
        self.assertIn("<svg", html)

    def test_labelled_icon(self):
        html = render('{% icon "info" label="Catatan" %}')
        self.assertIn('role="img"', html)
        self.assertIn('aria-label="Catatan"', html)

    def test_unknown_icon_renders_nothing(self):
        self.assertEqual(render('{% icon "tidak-ada" %}'), "")

    def test_every_icon_renders(self):
        for name in ICONS:
            with self.subTest(name=name):
                self.assertIn("<svg", render("{% icon name %}", name=name))


class ControlFilterTests(SimpleTestCase):
    class DemoForm(forms.Form):
        name = forms.CharField(help_text="Bantuan")
        kind = forms.ChoiceField(choices=[("a", "A")])
        note = forms.CharField(required=False, widget=forms.Textarea)

    def test_classes_and_aria_for_invalid_field(self):
        form = self.DemoForm(data={"name": "", "kind": "a"})
        html = render("{{ form.name|control }}", form=form)
        self.assertIn('class="input is-invalid"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertIn("id_name_help", html)
        self.assertIn("id_name_error", html)

    def test_select_and_textarea_classes(self):
        form = self.DemoForm()
        self.assertIn('class="select"', render("{{ form.kind|control }}", form=form))
        self.assertIn('class="textarea"', render("{{ form.note|control }}", form=form))


class PageTests(TestCase):
    def test_landing_uses_base_layout(self):
        response = self.client.get(reverse("main:landing"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'name="csrf-token"')
        self.assertContains(response, 'class="skip-link"')
        self.assertContains(response, 'id="toast-region"')
        self.assertContains(response, 'lang="id"')

    @override_settings(DEBUG=True)
    def test_styleguide_available_in_debug(self):
        response = self.client.get(reverse("main:styleguide"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Rujukan komponen")

    def test_styleguide_hidden_when_not_debug(self):
        self.assertEqual(self.client.get(reverse("main:styleguide")).status_code, 404)

    def test_friendly_404(self):
        response = self.client.get("/tidak-ada-halaman-ini/")
        self.assertContains(response, "Halaman tidak ditemukan", status_code=404)

    def test_friendly_403(self):
        request = RequestFactory().get("/rahasia/")
        request.user = AnonymousUser()
        response = permission_denied(request, Exception("tes"))
        self.assertEqual(response.status_code, 403)
        self.assertIn("Halaman ini butuh izin khusus", response.content.decode())

    def test_500_is_standalone(self):
        response = server_error(RequestFactory().get("/"))
        body = response.content.decode()
        self.assertEqual(response.status_code, 500)
        self.assertIn("Terjadi kesalahan di server", body)
        self.assertNotIn("<link", body)  # tidak bergantung pada file static

    def test_csrf_failure_page(self):
        client = Client(enforce_csrf_checks=True)
        response = client.post(f"/{settings.ADMIN_URL}login/", {"username": "x", "password": "y"})
        self.assertContains(response, "Formulir sudah kedaluwarsa", status_code=403)

    def test_django_messages_render_as_toast(self):
        html = render_to_string(
            "base.html",
            {"messages": [Message(constants.SUCCESS, "Shelf tersimpan"), Message(constants.ERROR, "Gagal menyimpan")]},
        )
        self.assertIn("toast--success", html)
        self.assertIn("Shelf tersimpan", html)
        self.assertIn('role="alert"', html)  # error memakai role alert
