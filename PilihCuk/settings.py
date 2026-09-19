"""
Settings proyek PilihCuk (Django 5.2).

Satu file dengan flag PRODUCTION:
- PRODUCTION=False (default) -> SQLite, DEBUG aktif, dibaca dari file .env
- PRODUCTION=True            -> PostgreSQL (PWS), DEBUG mati; semua variabel
                                diisi lewat environment variable di dashboard PWS
"""
import os
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Hanya .env yang dibaca kode. .env.prod cuma catatan untuk ditempel ke PWS.
load_dotenv(BASE_DIR / ".env")


def env_bool(name, default=False):
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name):
    return [item.strip() for item in os.getenv(name, "").split(",") if item.strip()]


PRODUCTION = env_bool("PRODUCTION", False)
DEBUG = not PRODUCTION

# Nama produk yang tampil di antarmuka (dipakai template mulai Bagian A.2).
SITE_NAME = os.getenv("SITE_NAME", "PilihCuk")

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    if PRODUCTION:
        raise ImproperlyConfigured("SECRET_KEY wajib diisi saat PRODUCTION=True.")
    SECRET_KEY = "dev-only-insecure-key-jangan-dipakai-di-server"

ALLOWED_HOSTS = ["localhost", "127.0.0.1"] + env_list("ALLOWED_HOSTS")
# Contoh: https://namamu-pilihcuk.pbp.cs.ui.ac.id (lengkap dengan https://)
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")

# URL Django admin (darurat, hanya superuser). Wajib diakhiri "/".
ADMIN_URL = os.getenv("ADMIN_URL", "kelola-darurat/")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    # Aplikasi PilihCuk
    "main",
    "accounts",
    "catalog",
    "shelves",
    "substitutions",
    "dataqueue",
    "preferences",
    "kurator",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "PilihCuk.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "PilihCuk.wsgi.application"

# Database
if PRODUCTION:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.getenv("DB_NAME"),
            "USER": os.getenv("DB_USER"),
            "PASSWORD": os.getenv("DB_PASSWORD"),
            "HOST": os.getenv("DB_HOST"),
            "PORT": os.getenv("DB_PORT"),
            "OPTIONS": {"options": f"-c search_path={os.getenv('SCHEMA', 'public')}"},
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Autentikasi (nama URL dibuat di Bagian B)
LOGIN_URL = "accounts:login"
LOGIN_REDIRECT_URL = "main:landing"
LOGOUT_REDIRECT_URL = "main:landing"

# Internasionalisasi
LANGUAGE_CODE = "id"
TIME_ZONE = "Asia/Jakarta"
USE_I18N = True
USE_TZ = True

# Static files (dilayani WhiteNoise di server)
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

if PRODUCTION:
    STORAGES = {
        "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
        },
    }
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    # SECURE_SSL_REDIRECT dan HSTS diaktifkan di Bagian K setelah HTTPS terverifikasi.

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Email (dev: dicetak ke konsol; dipakai fitur lupa password di Bagian B)
EMAIL_BACKEND = os.getenv(
    "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
)
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", f"{SITE_NAME} <no-reply@pilihcuk.local>")

# Open Food Facts (dipakai di Bagian D)
OFF_USER_AGENT = os.getenv(
    "OFF_USER_AGENT", "PilihCuk/0.1 (tugas kuliah PBP Fasilkom UI)"
)