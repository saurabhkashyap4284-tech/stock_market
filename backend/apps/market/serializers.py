# Serializers for market data
from rest_framework import serializers
from .models import Stock, OISnapshot, Candle5Min


class StockSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Stock
        fields = ["id", "symbol", "name", "is_index", "is_active"]


class OISnapshotSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="stock.symbol", read_only=True)
    oi_change_pct = serializers.SerializerMethodField()

    class Meta:
        model  = OISnapshot
        fields = [
            "id", "symbol", "timestamp", "date",
            "prev_close", "ltp", "open_price", "high", "low",
            "oi_current", "oi_previous", "oi_change", "oi_change_pct",
            "volume",
        ]

    def get_oi_change_pct(self, obj):
        if obj.oi_previous:
            return round((obj.oi_current - obj.oi_previous) / obj.oi_previous * 100, 2)
        return 0


class Candle5MinSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="stock.symbol", read_only=True)

    class Meta:
        model  = Candle5Min
        fields = [
            "id", "symbol", "date",
            "open_price", "high", "low", "close_price",
            "prev_close",
            "all_below_prev_close", "all_above_prev_close",
            "created_at",
        ]


class LiveStockSerializer(serializers.Serializer):
    """
    Redis se live data ke liye — DB model nahi, plain dict serialize karta hai.
    """
    symbol     = serializers.CharField()
    prev_close = serializers.FloatField()
    ltp        = serializers.FloatField()
    open       = serializers.FloatField(allow_null=True)
    high       = serializers.FloatField(allow_null=True)
    low        = serializers.FloatField(allow_null=True)
    oi_change  = serializers.FloatField(allow_null=True)
    volume     = serializers.IntegerField(allow_null=True)
    candle     = serializers.DictField(allow_null=True)
    signal     = serializers.DictField(allow_null=True)