from django.urls import path

from . import views

app_name = "main"

urlpatterns = [
    path("", views.landing, name="landing"),
    path("_styleguide/", views.styleguide, name="styleguide"),
]
