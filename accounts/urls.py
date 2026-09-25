from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    path("daftar/", views.register, name="register"),
    path("masuk/", views.LoginView.as_view(), name="login"),
    path("keluar/", views.logout, name="logout"),
]