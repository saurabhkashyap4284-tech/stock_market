from django.contrib.auth.models import AbstractUser
from django.db import models


class CustomUser(AbstractUser):
    """Extended user with watchlist support."""
    email      = models.EmailField(unique=True)
    phone      = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD  = "email"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return self.email


class Watchlist(models.Model):
    """User ki personal watchlist."""
    user       = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="watchlists")
    name       = models.CharField(max_length=50, default="My Watchlist")
    symbols    = models.JSONField(default=list)   # ["RELIANCE", "SBIN", ...]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.email} — {self.name}"

    class Meta:
        unique_together = ["user", "name"]