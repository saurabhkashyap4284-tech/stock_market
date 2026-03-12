from django.contrib import admin
from .models import Stock, OISnapshot, Candle5Min


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display  = ["symbol", "name", "is_index", "is_active", "created_at"]
    list_filter   = ["is_index", "is_active"]
    search_fields = ["symbol", "name"]
    ordering      = ["symbol"]


@admin.register(OISnapshot)
class OISnapshotAdmin(admin.ModelAdmin):
    list_display  = ["stock", "timestamp", "ltp", "oi_current", "oi_change", "volume"]
    list_filter   = ["date", "stock"]
    search_fields = ["stock__symbol"]
    ordering      = ["-timestamp"]
    readonly_fields = ["timestamp"]


@admin.register(Candle5Min)
class Candle5MinAdmin(admin.ModelAdmin):
    list_display  = [
        "stock", "date", "open_price", "high", "low", "close_price",
        "prev_close", "all_below_prev_close", "all_above_prev_close"
    ]
    list_filter   = ["date", "all_below_prev_close", "all_above_prev_close"]
    search_fields = ["stock__symbol"]
    ordering      = ["-date", "stock__symbol"]