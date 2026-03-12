"""
Signal Engine — Core Logic
==========================

BEARISH setup:
  - 5-min candle ke saare 4 points (O, H, L, C) prev_close se NICHE
  - OI badha = fresh shorts aa rahe hain
  - 9:20-9:30 mein price Open→High ke beech = dead-cat bounce (short karo)

BULLISH setup (exact mirror):
  - 5-min candle ke saare 4 points (O, H, L, C) prev_close se UPAR
  - OI badha = fresh longs aa rahe hain
  - 9:20-9:30 mein price Low→Open ke beech = healthy pullback (long karo)
"""


def classify_signal(stock: dict, candle5: dict, phase: str) -> dict:
    """
    Main signal classification function.

    Args:
        stock:   { prev_close, ltp, oi, oi_prev, ... }
        candle5: { open, high, low, close }
        phase:   PRE | CANDLE | WATCH | OPEN

    Returns:
        { signal, strength, reason }
    """
    # Sirf WATCH aur OPEN phase mein signals
    if not candle5 or phase in ("PRE", "CANDLE", "CLOSED"):
        return {"signal": "NEUTRAL", "strength": "-", "reason": "Market phase active nahi hai"}

    prev_close = stock["prev_close"]
    ltp        = stock["ltp"]
    oi         = stock.get("oi", 0)
    oi_prev    = stock.get("oi_prev", 0)
    oi_up      = oi > oi_prev

    c_open  = candle5["open"]
    c_high  = candle5["high"]
    c_low   = candle5["low"]
    c_close = candle5["close"]

    # ════════════════════════════════════════════════════════
    #  BEARISH — saare 4 points prev_close se NICHE
    # ════════════════════════════════════════════════════════
    full_bearish = (
        c_open  < prev_close and
        c_high  < prev_close and
        c_low   < prev_close and
        c_close < prev_close
    )

    if full_bearish and oi_up:
        # Price dead-cat bounce kar raha hai Open→High ke beech
        if c_open < ltp < c_high:
            return {
                "signal":   "BEARISH_TRAP",
                "strength": "STRONG",
                "reason":   (
                    f"OHLC sab < PrevClose({prev_close}) | OI↑ | "
                    f"LTP({ltp}) Open({c_open})→High({c_high}) ke beech = "
                    f"dead-cat bounce, short opportunity"
                ),
            }
        return {
            "signal":   "BEARISH",
            "strength": "STRONG",
            "reason":   f"OHLC sab < PrevClose({prev_close}) | OI↑ = fresh shorts build ho rahe",
        }

    if full_bearish and not oi_up:
        if c_open < ltp < c_high:
            return {
                "signal":   "BEARISH_TRAP",
                "strength": "MODERATE",
                "reason":   f"OHLC sab < PrevClose({prev_close}) | OI confirm nahi | LTP Open→High zone mein",
            }
        return {
            "signal":   "BEARISH",
            "strength": "MODERATE",
            "reason":   f"OHLC sab < PrevClose({prev_close}) | OI abhi confirm nahi kar raha",
        }

    # ════════════════════════════════════════════════════════
    #  BULLISH — saare 4 points prev_close se UPAR (exact mirror)
    # ════════════════════════════════════════════════════════
    full_bullish = (
        c_open  > prev_close and
        c_high  > prev_close and
        c_low   > prev_close and
        c_close > prev_close
    )

    if full_bullish and oi_up:
        # Price pullback kar raha hai Low→Open ke beech
        if c_low < ltp < c_open:
            return {
                "signal":   "BULLISH_PULLBACK",
                "strength": "STRONG",
                "reason":   (
                    f"OHLC sab > PrevClose({prev_close}) | OI↑ | "
                    f"LTP({ltp}) Low({c_low})→Open({c_open}) ke beech = "
                    f"healthy pullback, long opportunity"
                ),
            }
        return {
            "signal":   "BULLISH",
            "strength": "STRONG",
            "reason":   f"OHLC sab > PrevClose({prev_close}) | OI↑ = fresh longs build ho rahe",
        }

    if full_bullish and not oi_up:
        if c_low < ltp < c_open:
            return {
                "signal":   "BULLISH_PULLBACK",
                "strength": "MODERATE",
                "reason":   f"OHLC sab > PrevClose({prev_close}) | OI confirm nahi | LTP Low→Open zone mein",
            }
        return {
            "signal":   "BULLISH",
            "strength": "MODERATE",
            "reason":   f"OHLC sab > PrevClose({prev_close}) | OI abhi confirm nahi kar raha",
        }

    # ════════════════════════════════════════════════════════
    #  MIXED CANDLE — watch window mein price action
    # ════════════════════════════════════════════════════════
    if phase in ("WATCH", "OPEN"):
        if ltp < c_low:
            return {
                "signal":   "BEARISH",
                "strength": "STRONG" if oi_up else "MODERATE",
                "reason":   f"LTP({ltp}) 5-min Low({c_low}) se neeche breakdown | {'OI↑' if oi_up else 'OI confirm nahi'}",
            }
        if ltp > c_high:
            return {
                "signal":   "BULLISH",
                "strength": "STRONG" if oi_up else "MODERATE",
                "reason":   f"LTP({ltp}) 5-min High({c_high}) se upar breakout | {'OI↑' if oi_up else 'OI confirm nahi'}",
            }
        if c_open < ltp < c_high:
            return {
                "signal":   "BEARISH_ZONE",
                "strength": "WATCH",
                "reason":   f"LTP({ltp}) Open({c_open})→High({c_high}) ke beech | rejection ka wait karo",
            }
        if c_low < ltp < c_open:
            return {
                "signal":   "BULLISH_ZONE",
                "strength": "WATCH",
                "reason":   f"LTP({ltp}) Low({c_low})→Open({c_open}) ke beech | bounce ka wait karo",
            }

    return {"signal": "NEUTRAL", "strength": "-", "reason": "Abhi koi clear setup nahi"}