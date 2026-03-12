from datetime import datetime
import pytz

IST = pytz.timezone("Asia/Kolkata")


def get_market_phase(now: datetime = None) -> str:
    """
    Market phase detect karo current time se.

    PRE    → 9:15 se pehle
    CANDLE → 9:15 to 9:20  (5-min candle build ho rahi hai)
    WATCH  → 9:20 to 9:30  (signals fire hote hain)
    OPEN   → 9:30 ke baad  (normal trading)
    CLOSED → 3:30 ke baad
    """
    if now is None:
        now = datetime.now(IST)

    # IST mein convert karo
    if now.tzinfo is None:
        now = IST.localize(now)
    else:
        now = now.astimezone(IST)

    h, m = now.hour, now.minute
    total_mins = h * 60 + m

    if total_mins < 9 * 60 + 15:
        return "PRE"
    elif total_mins < 9 * 60 + 20:
        return "CANDLE"
    elif total_mins < 9 * 60 + 30:
        return "WATCH"
    elif total_mins < 15 * 60 + 30:
        return "OPEN"
    else:
        return "CLOSED"


def is_market_hours(now: datetime = None) -> bool:
    """Kya abhi market data fetch karna chahiye?"""
    phase = get_market_phase(now)
    return phase in ("CANDLE", "WATCH", "OPEN")


def is_trading_day(now: datetime = None) -> bool:
    """Weekday check — Saturday/Sunday ko fetch mat karo."""
    if now is None:
        now = datetime.now(IST)
    return now.weekday() < 5 