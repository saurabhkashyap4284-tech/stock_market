import json
import redis
from django.conf import settings

# Single shared connection pool
_client = None

def get_redis():
    global _client
    if _client is None:
        _client = redis.from_url(settings.REDIS_URL, decode_responses=True)
    return _client


# ── Key naming convention ─────────────────────────────────────────
class RedisKeys:
    STOCK_DATA   = "market:stock:{symbol}"          # latest tick per stock
    CANDLE_5MIN  = "market:candle5:{symbol}"        # 5-min OHLC
    SIGNAL       = "market:signal:{symbol}"         # current signal
    PHASE        = "market:phase"                   # current market phase
    ALL_SYMBOLS  = "market:symbols"                 # set of all symbols
    PREV_CLOSE   = "market:prev_close:{symbol}"     # previous close cache
    DATA_HASH    = "market:data_hash"               # MD5 of latest API response
    BASELINE_LTP = "market:baseline_ltp:{symbol}"   # 9 AM reference LTP
    BASELINE_OI  = "market:baseline_oi:{symbol}"    # 9 AM reference OI


# ── Helpers ───────────────────────────────────────────────────────
def set_stock(symbol: str, data: dict, ttl: int = 120):
    """Save latest stock tick to Redis."""
    r = get_redis()
    key = RedisKeys.STOCK_DATA.format(symbol=symbol)
    r.setex(key, ttl, json.dumps(data))


def get_stock(symbol: str) -> dict | None:
    r = get_redis()
    raw = r.get(RedisKeys.STOCK_DATA.format(symbol=symbol))
    return json.loads(raw) if raw else None


def set_candle(symbol: str, ohlc: dict):
    """Save 5-min candle — no TTL, needed all day."""
    r = get_redis()
    r.set(RedisKeys.CANDLE_5MIN.format(symbol=symbol), json.dumps(ohlc))


def get_candle(symbol: str) -> dict | None:
    r = get_redis()
    raw = r.get(RedisKeys.CANDLE_5MIN.format(symbol=symbol))
    return json.loads(raw) if raw else None


def set_signal(symbol: str, signal: dict):
    r = get_redis()
    r.set(RedisKeys.SIGNAL.format(symbol=symbol), json.dumps(signal))


def get_signal(symbol: str) -> dict | None:
    r = get_redis()
    raw = r.get(RedisKeys.SIGNAL.format(symbol=symbol))
    return json.loads(raw) if raw else None


def set_phase(phase: str):
    get_redis().set(RedisKeys.PHASE, phase)


def get_phase() -> str:
    return get_redis().get(RedisKeys.PHASE) or "PRE"


def register_symbol(symbol: str):
    get_redis().sadd(RedisKeys.ALL_SYMBOLS, symbol)


def get_all_symbols() -> set:
    return get_redis().smembers(RedisKeys.ALL_SYMBOLS)


def publish(channel: str, data: dict):
    """Pub/Sub — broadcast to all subscribers."""
    get_redis().publish(channel, json.dumps(data))


def set_prev_close(symbol: str, price: float):
    """Cache previous close for the day."""
    key = RedisKeys.PREV_CLOSE.format(symbol=symbol)
    get_redis().set(key, price)

def get_prev_close(symbol: str) -> float | None:
    key = RedisKeys.PREV_CLOSE.format(symbol=symbol)
    val = get_redis().get(key)
    return float(val) if val else None

def set_data_hash(h: str):
    get_redis().set(RedisKeys.DATA_HASH, h)

def get_data_hash() -> str | None:
    return get_redis().get(RedisKeys.DATA_HASH)

def clear_market_state():
    """Daily reset — clear candles, signals, and baselines."""
    r = get_redis()
    keys = (
        r.keys("market:candle5:*") +
        r.keys("market:signal:*") +
        r.keys("market:baseline_ltp:*") +
        r.keys("market:baseline_oi:*")
    )
    if keys:
        r.delete(*keys)


# ── Baseline (9 AM reference) ────────────────────────────────────
def set_baseline_ltp(symbol: str, ltp: float):
    """Store 9 AM LTP baseline for signal comparison."""
    key = RedisKeys.BASELINE_LTP.format(symbol=symbol)
    get_redis().set(key, ltp)

def get_baseline_ltp(symbol: str) -> float | None:
    key = RedisKeys.BASELINE_LTP.format(symbol=symbol)
    val = get_redis().get(key)
    return float(val) if val else None

def set_baseline_oi(symbol: str, oi: int):
    """Store 9 AM OI baseline for signal comparison."""
    key = RedisKeys.BASELINE_OI.format(symbol=symbol)
    get_redis().set(key, oi)

def get_baseline_oi(symbol: str) -> int | None:
    key = RedisKeys.BASELINE_OI.format(symbol=symbol)
    val = get_redis().get(key)
    return int(val) if val else None