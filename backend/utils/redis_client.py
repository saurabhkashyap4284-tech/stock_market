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