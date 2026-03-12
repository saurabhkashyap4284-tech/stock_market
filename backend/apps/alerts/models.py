# apps/alerts/models.py
from django.db import models
from apps.market.models import Stock
from apps.users.models import CustomUser


class AlertRule(models.Model):
    """
    User define karta hai — kaunse signal pe alert chahiye.
    Example: RELIANCE pe BEARISH STRONG signal aaye to email bhejo.
    """
    SIGNAL_CHOICES = [
        ("BEARISH",          "Bearish"),
        ("BEARISH_TRAP",     "Bearish Trap"),
        ("BULLISH",          "Bullish"),
        ("BULLISH_PULLBACK", "Bullish Pullback"),
        ("ANY",              "Any Signal"),
    ]

    user        = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="alert_rules")
    stock       = models.ForeignKey(Stock, on_delete=models.CASCADE, null=True, blank=True,
                                    help_text="Null = all stocks")
    signal_type = models.CharField(max_length=20, choices=SIGNAL_CHOICES, default="ANY")
    only_strong = models.BooleanField(default=True,  help_text="Sirf STRONG signals pe alert")
    via_email   = models.BooleanField(default=True)
    is_active   = models.BooleanField(default=True)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        stock_name = self.stock.symbol if self.stock else "All Stocks"
        return f"{self.user.email} | {stock_name} | {self.signal_type}"


class AlertLog(models.Model):
    """Har sent alert ka record."""
    user        = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rule        = models.ForeignKey(AlertRule, on_delete=models.SET_NULL, null=True)
    stock       = models.ForeignKey(Stock, on_delete=models.CASCADE)
    signal_type = models.CharField(max_length=20)
    strength    = models.CharField(max_length=10)
    ltp         = models.FloatField()
    sent_at     = models.DateTimeField(auto_now_add=True)
    delivered   = models.BooleanField(default=False)

    class Meta:
        ordering = ["-sent_at"]