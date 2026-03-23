from django.test import TestCase
from apps.market.services.signal_engine import classify_signal


class SignalEngineTests(TestCase):
    def setUp(self):
        self.baseline_ltp = 100.0
        self.baseline_oi  = 1000
        self.stock = {
            "symbol": "TEST",
            "ltp": 105.0,
            "prev_close": 100.0,
            "oi": 1100,     # OI increased vs baseline
            "oi_prev": 900
        }
        self.candle = {
            "open": 101.0,
            "high": 106.0,
            "low": 100.5,
            "close": 105.0
        }
        self.phase = "WATCH"

    def test_bearish_signal(self):
        """LTP < baseline AND LTP < candle_high AND OI increased → BEARISH"""
        self.stock["ltp"] = 95.0   # Below baseline (100)
        self.stock["oi"] = 1200    # OI increased vs baseline (1000)
        sig = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig["signal"], "BEARISH")

    def test_bullish_signal(self):
        """LTP > baseline AND candle_low <= LTP <= candle_high → BULLISH"""
        self.stock["ltp"] = 103.0  # Above baseline and within candle range
        sig = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig["signal"], "BULLISH")

    def test_false_alert_bull(self):
        """Was BULLISH, then LTP drops below baseline → FALSE_ALERT_BULL"""
        # Step 1: Get bullish signal first
        self.stock["ltp"] = 103.0
        sig1 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig1["signal"], "BULLISH")

        # Step 2: LTP drops below baseline
        self.stock["ltp"] = 95.0
        sig2 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi,
            current_signal=sig1
        )
        self.assertEqual(sig2["signal"], "FALSE_ALERT_BULL")

    def test_false_alert_bear(self):
        """Was BEARISH, then LTP rises above baseline → FALSE_ALERT_BEAR"""
        # Step 1: Get bearish signal
        self.stock["ltp"] = 95.0
        self.stock["oi"] = 1200
        sig1 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig1["signal"], "BEARISH")

        # Step 2: LTP goes above baseline
        self.stock["ltp"] = 105.0
        sig2 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi,
            current_signal=sig1
        )
        self.assertEqual(sig2["signal"], "FALSE_ALERT_BEAR")

    def test_false_alert_is_sticky(self):
        """Once a signal becomes FALSE_ALERT, it stays that way for the day"""
        # Step 1: Bullish
        self.stock["ltp"] = 103.0
        sig1 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        # Step 2: False alert
        self.stock["ltp"] = 95.0
        sig2 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi,
            current_signal=sig1
        )
        self.assertEqual(sig2["signal"], "FALSE_ALERT_BULL")

        # Step 3: Price recovers — should STILL be false alert
        self.stock["ltp"] = 108.0
        sig3 = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi,
            current_signal=sig2
        )
        self.assertEqual(sig3["signal"], "FALSE_ALERT_BULL")

    def test_neutral_no_candle(self):
        """No candle data → NEUTRAL"""
        sig = classify_signal(
            self.stock, None, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig["signal"], "NEUTRAL")

    def test_neutral_pre_market(self):
        """PRE phase → NEUTRAL regardless of data"""
        sig = classify_signal(
            self.stock, self.candle, "PRE",
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig["signal"], "NEUTRAL")

    def test_neutral_no_clear_setup(self):
        """LTP above baseline but OUTSIDE candle range → NEUTRAL"""
        self.stock["ltp"] = 110.0  # Above candle high (106)
        sig = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        self.assertEqual(sig["signal"], "NEUTRAL")

    def test_bearish_requires_oi_increase(self):
        """Bearish conditions but OI NOT increased → NOT bearish"""
        self.stock["ltp"] = 95.0
        self.stock["oi"] = 900  # OI decreased vs baseline (1000)
        sig = classify_signal(
            self.stock, self.candle, self.phase,
            baseline_ltp=self.baseline_ltp,
            baseline_oi=self.baseline_oi
        )
        # Should be NEUTRAL because OI didn't increase
        self.assertEqual(sig["signal"], "NEUTRAL")
