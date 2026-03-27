import logging

logger = logging.getLogger(__name__)


def classify_signal(
    stock: dict,
    candle5: dict,
    phase: str,
    baseline_ltp: float = None,
    baseline_oi: int = None,
    current_signal: dict = None,
) -> dict:
    """
    Signal classification based on user requirements:

    BEARISH:
        - LTP < baseline_ltp (9 AM / prev_close)
        - LTP < 5-min candle high
        - OI increased vs baseline_oi

    BULLISH:
        - LTP > baseline_ltp (9 AM / prev_close)
        - LTP within 5-min candle range (between low and high)

    FALSE_ALERT_BULL:
        - Was previously BULLISH but LTP dropped below baseline_ltp

    FALSE_ALERT_BEAR:
        - Was previously BEARISH but LTP rose above baseline_ltp
    """
    # Carry forward previous state
    prev_signal_type = current_signal.get("signal", "NEUTRAL") if current_signal else "NEUTRAL"
    signal_ts        = current_signal.get("signal_ts") if current_signal else None

    # Not ready yet — no candle or not in active phase
    if not candle5 or phase in ("PRE", "CANDLE", "CLOSED"):
        return {
            "signal":     "NEUTRAL",
            "reason":     "Market not in active phase or candle missing",
            "signal_ts":  signal_ts,
        }

    # No baseline available — can't classify
    if baseline_ltp is None:
        return {
            "signal":     "NEUTRAL",
            "reason":     "Baseline LTP not available yet",
            "signal_ts":  signal_ts,
        }

    ltp        = stock["ltp"]
    oi_current = stock.get("oi", 0)
    c_high     = candle5["high"]
    c_low      = candle5["low"]

    # OI comparison
    oi_increased = False
    if baseline_oi and baseline_oi > 0:
        oi_increased = oi_current > baseline_oi


    # ════════════════════════════════════════════════════════
    #  FAILED SIGNAL Detection (sticky invalidation)
    # ════════════════════════════════════════════════════════

    # Was BULLISH_BREAKOUT, now LTP fell below baseline → Bullish Failed
    if prev_signal_type == "BULLISH_BREAKOUT" and ltp < baseline_ltp:
        return {
            "signal":     "BULLISH_FAILED",
            "reason":     f"Was Bullish, reversed below baseline | LTP({ltp}) < Baseline({baseline_ltp})",
            "signal_ts":  None,
        }

    # Was BEARISH_FALL, now LTP rose above baseline → Bearish Failed
    if prev_signal_type == "BEARISH_FALL" and ltp > baseline_ltp:
        return {
            "signal":     "BEARISH_FAILED",
            "reason":     f"Was Bearish, reversed above baseline | LTP({ltp}) > Baseline({baseline_ltp})",
            "signal_ts":  None,
        }

    # "FAILED" signals are sticky for the day
    if prev_signal_type in ("BULLISH_FAILED", "BEARISH_FAILED"):
        return {
            "signal":     prev_signal_type,
            "reason":     current_signal.get("reason", "Signal invalidated earlier"),
            "signal_ts":  signal_ts,
        }

    # ════════════════════════════════════════════════════════
    #  BEARISH FALL — LTP < baseline AND LTP < candle high AND OI ↑
    # ════════════════════════════════════════════════════════
    if ltp < baseline_ltp and ltp < c_high and oi_increased:
        return {
            "signal":     "BEARISH_FALL",
            "reason":     f"LTP({ltp}) < Baseline({baseline_ltp}) & < Candle High({c_high}) | OI↑",
            "signal_ts":  signal_ts if prev_signal_type == "BEARISH_FALL" else None,
        }

    # ════════════════════════════════════════════════════════
    #  BULLISH BREAKOUT — LTP > baseline AND LTP > candle low
    # ════════════════════════════════════════════════════════
    if ltp > baseline_ltp and ltp >= c_low:
        # We classify as BULLISH_BREAKOUT if it's above baseline and within/above candle range
        return {
            "signal":     "BULLISH_BREAKOUT",
            "reason":     f"LTP({ltp}) > Baseline({baseline_ltp}) & in/above range [{c_low}, {c_high}]",
            "signal_ts":  signal_ts if prev_signal_type == "BULLISH_BREAKOUT" else None,
        }

    # ════════════════════════════════════════════════════════
    #  NEUTRAL — No clear setup
    # ════════════════════════════════════════════════════════
    return {
        "signal":     "NEUTRAL",
        "reason":     f"No clear signal | LTP={ltp}, Baseline={baseline_ltp}, Candle=[{c_low}-{c_high}]",
        "signal_ts":  signal_ts,
    }