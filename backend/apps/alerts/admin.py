from django.contrib import admin
from .models import AlertRule, AlertLog


@admin.register(AlertRule)
class AlertRuleAdmin(admin.ModelAdmin):
    list_display  = ["user", "stock", "signal_type", "only_strong", "via_email", "is_active"]
    list_filter   = ["signal_type", "is_active", "via_email"]
    search_fields = ["user__email", "stock__symbol"]


@admin.register(AlertLog)
class AlertLogAdmin(admin.ModelAdmin):
    list_display  = ["user", "stock", "signal_type", "strength", "ltp", "sent_at", "delivered"]
    list_filter   = ["signal_type", "delivered"]
    search_fields = ["user__email", "stock__symbol"]
    ordering      = ["-sent_at"]
    readonly_fields = ["sent_at"]