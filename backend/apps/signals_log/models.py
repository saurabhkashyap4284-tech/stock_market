# apps/signals_log/models.py
from django.db import models
from apps.market.models import Stock


class SignalEvent(models.Model):
    """
    Har signal fire hone pe ek record — history track karne ke liye.
    """
    SIGNAL_CHOICES = [
        ("BEARISH",          "Bearish"),
        ("BEARISH_TRAP",     "Bearish Trap"),
        ("BEARISH_ZONE",     "Bearish Zone"),
        ("BULLISH",          "Bullish"),
        ("BULLISH_PULLBACK", "Bullish Pullback"),
        ("BULLISH_ZONE",     "Bullish Zone"),
        ("NEUTRAL",          "Neutral"),
    ]

    STRENGTH_CHOICES = [
        ("STRONG",   "Strong"),
        ("MODERATE", "Moderate"),
        ("WATCH",    "Watch"),
        ("-",        "None"),
    ]

    PHASE_CHOICES = [
        ("PRE",    "Pre Market"),
        ("CANDLE", "5-Min Candle"),
        ("WATCH",  "Watch Window"),
        ("OPEN",   "Market Open"),
    ]

    stock       = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="signal_events")
    date        = models.DateField(db_index=True)
    signal_type = models.CharField(max_length=20, choices=SIGNAL_CHOICES, db_index=True)
    strength    = models.CharField(max_length=10, choices=STRENGTH_CHOICES)
    reason      = models.TextField()
    ltp         = models.FloatField()
    phase       = models.CharField(max_length=10, choices=PHASE_CHOICES)
    created_at  = models.DateTimeField(auto_now_add=True, db_index=True)

    def __str__(self):
        return f"{self.stock.symbol} | {self.signal_type} | {self.created_at}"

    class Meta:
        ordering = ["-created_at"]
        indexes  = [models.Index(fields=["date", "signal_type"])]