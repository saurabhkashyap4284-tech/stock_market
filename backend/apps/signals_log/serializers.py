from rest_framework import serializers
from .models import SignalEvent


class SignalEventSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source='stock.symbol', read_only=True)
    
    class Meta:
        model = SignalEvent
        fields = [
            'id', 'symbol', 'date', 'signal_type', 'strength',
            'reason', 'ltp', 'phase', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SignalSummarySerializer(serializers.Serializer):
    """Summary of signal counts"""
    total = serializers.IntegerField()
    bearish = serializers.IntegerField()
    bearish_trap = serializers.IntegerField()
    bearish_zone = serializers.IntegerField()
    bullish = serializers.IntegerField()
    bullish_pullback = serializers.IntegerField()
    bullish_zone = serializers.IntegerField()
    neutral = serializers.IntegerField()

# ── serializers.py ───────────────────────────────────────────────
from rest_framework import serializers
from .models import SignalEvent


class SignalEventSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(source="stock.symbol", read_only=True)

    class Meta:
        model  = SignalEvent
        fields = [
            "id", "symbol", "date", "signal_type", "strength",
            "reason", "ltp", "phase", "created_at",
        ]