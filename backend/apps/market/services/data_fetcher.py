import random
import logging
import requests
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_market_data() -> list[dict]:
    """
    Market data fetch karo.
    USE_MOCK_DATA=True → mock data
    USE_MOCK_DATA=False → real API
    """
    if settings.USE_MOCK_DATA:
        return _fetch_mock()
    return _fetch_real_api()


from .nse_service import nse_service

from utils.redis_client import get_prev_close

# ── Real API (NSE India) ──────────────────────────────────────────
def _fetch_real_api() -> list[dict]:
    """
    NSE F&O API se data fetch karo aur map karo.
    Merge FO Securities (all 200) with OI Spurts (active OI changes).
    """
    # 1. Fetch all F&O securities for base price data
    fo_data = nse_service.fetch_fo_securities()
    # 2. Fetch OI spurts for OI data
    oi_data = nse_service.fetch_oi_spurts()

    if not fo_data and not oi_data:
        return []

    # Map OI data by symbol for quick lookup
    oi_map = {item.get("symbol"): item for item in oi_data if item.get("symbol")}

    processed = []
    
    # Process the full F&O list
    for item in fo_data:
        try:
            symbol = item.get("symbol")
            if not symbol or symbol == "SECURITIES IN F&O":
                continue
                
            ltp = float(item.get("lastPrice", 0))
            prev_close = float(item.get("previousClose", 0))
            if prev_close == 0:
                prev_close = get_prev_close(symbol) or ltp
                
            open_price = float(item.get("open", 0))
            high_price = float(item.get("dayHigh", 0))
            low_price  = float(item.get("dayLow", 0))
            volume     = int(item.get("totalTradedVolume", 0))
            
            # Match with OI data
            oi_item = oi_map.get(symbol, {})
            
            processed.append({
                "symbol":     symbol,
                "ltp":        ltp,
                "prev_close": prev_close,
                "open":       open_price if open_price > 0 else None,
                "high":       high_price if high_price > 0 else None,
                "low":        low_price if low_price > 0 else None,
                "oi":         oi_item.get("latestOI", 0),
                "oi_prev":    oi_item.get("prevOI", 0),
                "oi_change":  oi_item.get("avgInOI", 0),
                "volume":     volume,
            })
            
            # Remove from map so we can process leftovers
            if symbol in oi_map:
                del oi_map[symbol]
                
        except Exception as e:
            logger.error(f"Error mapping FO item {item.get('symbol')}: {e}")
            continue
            
    # Process any remaining OI items that weren't in the FO list (rare)
    for symbol, item in oi_map.items():
        try:
            ltp = float(item.get("underlyingValue", 0))
            prev_close = get_prev_close(symbol) or ltp
            processed.append({
                "symbol":     symbol,
                "ltp":        ltp,
                "prev_close": prev_close,
                "open":       None,
                "high":       None,
                "low":        None,
                "oi":         item.get("latestOI", 0),
                "oi_prev":    item.get("prevOI", 0),
                "oi_change":  item.get("avgInOI", 0),
                "volume":     item.get("volume", 0),
            })
        except Exception as e:
            continue

    return processed


# ── Mock Data ─────────────────────────────────────────────────────
_mock_state = {}   # persist state between calls

_BASE_DATA = [
    dict(symbol="RELIANCE",   prev_close=1407, open=1390, high=1400, low=1382, ltp=1385, oi=2100000, oi_prev=1950000),
    dict(symbol="SBIN",       prev_close=1139, open=1089, high=1095, low=1080, ltp=1082, oi=5200000, oi_prev=4800000),
    dict(symbol="INFY",       prev_close=1311, open=1295, high=1305, low=1290, ltp=1298, oi=1800000, oi_prev=1750000),
    dict(symbol="HDFCBANK",   prev_close=857,  open=828,  high=835,  low=822,  ltp=826,  oi=3600000, oi_prev=3400000),
    dict(symbol="TCS",        prev_close=2560, open=2515, high=2530, low=2505, ltp=2510, oi=900000,  oi_prev=880000),
    dict(symbol="WIPRO",      prev_close=196,  open=193,  high=198,  low=191,  ltp=197,  oi=2200000, oi_prev=2100000),
    dict(symbol="ICICIBANK",  prev_close=1315, open=1263, high=1275, low=1255, ltp=1260, oi=4200000, oi_prev=3900000),
    dict(symbol="DMART",      prev_close=3881, open=3824, high=3850, low=3810, ltp=3840, oi=450000,  oi_prev=440000),
    dict(symbol="MCX",        prev_close=2541, open=2473, high=2500, low=2460, ltp=2490, oi=680000,  oi_prev=650000),
    dict(symbol="TORNTPHARM", prev_close=4325, open=4340, high=4380, low=4310, ltp=4375, oi=430000,  oi_prev=420000),
]


def _fetch_mock() -> list[dict]:
    global _mock_state
    result = []

    for base in _BASE_DATA:
        sym = base["symbol"]
        if sym not in _mock_state:
            _mock_state[sym] = dict(base)

        state = _mock_state[sym]

        # Random price drift
        drift   = (random.random() - 0.52) * 0.4
        new_ltp = round(state["ltp"] * (1 + drift / 100), 2)
        new_ltp = max(new_ltp, base["low"] * 0.95)
        state["ltp"]  = new_ltp
        state["high"] = max(state["high"], new_ltp)
        state["low"]  = min(state["low"],  new_ltp)

        # Random OI drift
        oi_factor     = 1.02 if random.random() > 0.4 else 0.99
        state["oi"]   = int(state["oi"] * oi_factor)
        oi_change_pct = round((state["oi"] - state["oi_prev"]) / state["oi_prev"] * 100, 2)

        result.append({
            "symbol":    sym,
            "prev_close":state["prev_close"],
            "ltp":       round(new_ltp, 2),
            "open":      state["open"],
            "high":      state["high"],
            "low":       state["low"],
            "oi":        state["oi"],
            "oi_prev":   state["oi_prev"],
            "oi_change": oi_change_pct,
            "volume":    random.randint(10000, 500000),
        })

    return result