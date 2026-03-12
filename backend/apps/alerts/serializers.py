from rest_framework import serializers
from .models import AlertRule, AlertLog


class AlertRuleSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source="stock.symbol", read_only=True, allow_null=True)

    class Meta:
        model  = AlertRule
        fields = [
            "id", "stock", "stock_symbol", "signal_type",
            "only_strong", "via_email", "is_active", "created_at",
        ]
        read_only_fields = ["created_at"]

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return super().create(validated_data)


class AlertLogSerializer(serializers.ModelSerializer):
    stock_symbol = serializers.CharField(source="stock.symbol", read_only=True)

    class Meta:
        model  = AlertLog
        fields = [
            "id", "stock_symbol", "signal_type", "strength",
            "ltp", "sent_at", "delivered",
        ]