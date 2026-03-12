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


# ── Real API (replace when ready) ────────────────────────────────
def _fetch_real_api() -> list[dict]:
    """
    Real API se data fetch karo.
    Expected response shape:
    {
      "data": [
        {
          "symbol": "RELIANCE",
          "prev_close": 1407,
          "ltp": 1395,
          "open": 1390,
          "high": 1400,
          "low": 1382,
          "oi": 2100000,
          "oi_prev": 1950000,
          "oi_change": 7.69,
          "volume": 520000
        },
        ...
      ]
    }
    """
    headers = {"Authorization": f"Bearer {settings.MARKET_API_KEY}"}
    resp    = requests.get(settings.MARKET_API_URL, headers=headers, timeout=10)
    resp.raise_for_status()
    return resp.json()["data"]


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