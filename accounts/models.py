from django.conf import settings
from django.db import models


class Profile(models.Model):
    class Role(models.TextChoices):
        USER = "user", "Pengguna"
        CURATOR = "curator", "Kurator"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    display_name = models.CharField("nama tampilan", max_length=60)
    role = models.CharField(
        max_length=10, choices=Role.choices, default=Role.USER, db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "profil"
        verbose_name_plural = "profil"

    def __str__(self):
        return f"{self.user.get_username()} ({self.get_role_display()})"

    @property
    def is_curator(self):
        return self.role == self.Role.CURATOR