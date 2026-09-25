"""Form autentikasi PilihCuk.

Pesan error validator sandi bawaan Django sudah diterjemahkan (LANGUAGE_CODE = "id"),
jadi tidak ditulis ulang di sini. Help text dan pesan khusus PilihCuk memakai nada
yang konsisten dengan bagian formulir lain.
"""
from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class RegisterForm(UserCreationForm):
    email = forms.EmailField(label="Email")
    display_name = forms.CharField(label="Nama tampilan", max_length=60)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    field_order = ["username", "email", "display_name", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username"
        self.fields["username"].help_text = "Dipakai untuk masuk. Huruf, angka, dan @/./+/-/_ saja."
        self.fields["email"].help_text = "Dipakai untuk memulihkan akun. Tidak ditampilkan ke pengguna lain."
        self.fields["display_name"].help_text = "Tampil di shelf dan usulan substitusimu."
        self.fields["password1"].label = "Kata sandi"
        self.fields["password1"].help_text = (
            "Minimal 8 karakter, tidak boleh angka semua, dan tidak boleh sama dengan username atau emailmu."
        )
        self.fields["password2"].label = "Konfirmasi kata sandi"
        self.fields["password2"].help_text = "Ketik ulang kata sandi yang sama, untuk memastikan tidak salah ketik."

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError("Email ini sudah dipakai akun lain. Masuk, atau pakai email lain.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
            user.profile.display_name = self.cleaned_data["display_name"]
            user.profile.save(update_fields=["display_name"])
        return user


class LoginForm(AuthenticationForm):
    """AuthenticationForm bawaan, dengan pesan error yang lebih ramah."""

    error_messages = {
        **AuthenticationForm.error_messages,
        "invalid_login": "Username atau kata sandi salah. Periksa lagi, lalu coba masuk sekali lagi.",
        "inactive": "Akun ini sudah dinonaktifkan. Hubungi Kurator data kalau ini keliru.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].label = "Username"
        self.fields["password"].label = "Kata sandi"
        self.fields["username"].widget.attrs.pop("autofocus", None)