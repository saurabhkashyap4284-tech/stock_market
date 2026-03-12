def update_candle(existing: dict, ltp: float, market_open: float) -> dict:
    """
    5-min candle update karo har tick pe.

    Args:
        existing:    Pehle se Redis mein jo candle hai (ya empty dict)
        ltp:         Latest traded price
        market_open: Market open price (9:15 ka pehla tick)

    Returns:
        Updated candle { open, high, low, close }
    """
    if not existing:
        # Pehla tick — candle shuru hoti hai
        return {
            "open":  market_open or ltp,
            "high":  ltp,
            "low":   ltp,
            "close": ltp,
        }

    return {
        "open":  existing["open"],                    # open fix rehta hai
        "high":  max(existing["high"], ltp),          # high update hota hai
        "low":   min(existing["low"],  ltp),          # low update hota hai
        "close": ltp,                                 # close = latest price
    }


def is_bearish_candle(candle: dict, prev_close: float) -> bool:
    """Kya saare 4 points prev_close se niche hain?"""
    return (
        candle["open"]  < prev_close and
        candle["high"]  < prev_close and
        candle["low"]   < prev_close and
        candle["close"] < prev_close
    )


def is_bullish_candle(candle: dict, prev_close: float) -> bool:
    """Kya saare 4 points prev_close se upar hain?"""
    return (
        candle["open"]  > prev_close and
        candle["high"]  > prev_close and
        candle["low"]   > prev_close and
        candle["close"] > prev_close
    )