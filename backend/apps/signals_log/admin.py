from django.contrib import admin
from .models import SignalEvent


@admin.register(SignalEvent)
class SignalEventAdmin(admin.ModelAdmin):
    list_display  = ["stock", "signal_type", "strength", "ltp", "phase", "created_at"]
    list_filter   = ["date", "signal_type", "strength", "phase"]
    search_fields = ["stock__symbol"]
    ordering      = ["-created_at"]
    readonly_fields = ["created_at"]