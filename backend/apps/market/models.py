from django.db import models


class Stock(models.Model):
    """Master list of all F&O stocks."""
    symbol       = models.CharField(max_length=30, unique=True)
    name         = models.CharField(max_length=100, blank=True)
    is_index     = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.symbol

    class Meta:
        ordering = ["symbol"]


class OISnapshot(models.Model):
    """
    Raw OI data saved every 30 seconds.
    Ye table historical analysis ke liye hai.
    """
    stock        = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="oi_snapshots")
    timestamp    = models.DateTimeField(auto_now_add=True, db_index=True)
    date         = models.DateField(db_index=True)

    # Price data
    prev_close   = models.FloatField()
    ltp          = models.FloatField()    # last traded price
    open_price   = models.FloatField()
    high         = models.FloatField()
    low          = models.FloatField()

    # OI data
    oi_current   = models.BigIntegerField()
    oi_previous  = models.BigIntegerField()
    oi_change    = models.FloatField()    # % change

    volume       = models.BigIntegerField(default=0)

    def __str__(self):
        return f"{self.stock.symbol} @ {self.timestamp}"

    class Meta:
        ordering        = ["-timestamp"]
        indexes         = [models.Index(fields=["stock", "date"])]
        get_latest_by   = "timestamp"


class Candle5Min(models.Model):
    """
    5-min candle (9:15 - 9:20) — ek din mein ek record per stock.
    Signal engine isi se kaam karta hai.
    """
    stock        = models.ForeignKey(Stock, on_delete=models.CASCADE, related_name="candles_5min")
    date         = models.DateField(db_index=True)

    open_price   = models.FloatField()
    high         = models.FloatField()
    low          = models.FloatField()
    close_price  = models.FloatField()

    prev_close   = models.FloatField()   # previous day close — comparison ke liye

    # Computed flags
    all_below_prev_close = models.BooleanField(default=False)  # bearish setup
    all_above_prev_close = models.BooleanField(default=False)  # bullish setup

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Auto-compute flags
        self.all_below_prev_close = (
            self.open_price  < self.prev_close and
            self.high        < self.prev_close and
            self.low         < self.prev_close and
            self.close_price < self.prev_close
        )
        self.all_above_prev_close = (
            self.open_price  > self.prev_close and
            self.high        > self.prev_close and
            self.low         > self.prev_close and
            self.close_price > self.prev_close
        )
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stock.symbol} 5min candle {self.date}"

    class Meta:
        unique_together = ["stock", "date"]   # ek din mein sirf ek candle
        ordering        = ["-date"]