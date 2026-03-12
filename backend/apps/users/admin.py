from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Watchlist


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display  = ["email", "username", "phone", "is_active", "date_joined"]
    search_fields = ["email", "username"]
    ordering      = ["-date_joined"]
    fieldsets     = UserAdmin.fieldsets + (
        ("Extra", {"fields": ("phone",)}),
    )


@admin.register(Watchlist)
class WatchlistAdmin(admin.ModelAdmin):
    list_display  = ["user", "name", "updated_at"]
    search_fields = ["user__email", "name"]