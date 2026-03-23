import logging
import hashlib
import json
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone
from datetime import timedelta

from utils.redis_client import (
    set_stock, get_stock, set_candle, get_candle,
    set_signal, get_signal, set_phase, get_phase,
    register_symbol, get_all_symbols,
    get_data_hash, set_data_hash,
    set_prev_close, clear_market_state,
    set_baseline_ltp, get_baseline_ltp,
    set_baseline_oi, get_baseline_oi,
)
from utils.time_utils import is_market_holiday
from apps.market.services.phase_detector import get_market_phase, is_trading_day
from apps.market.services.signal_engine import classify_signal
from apps.market.services.data_fetcher import fetch_market_data
from apps.market.services.candle_builder import update_candle
from apps.market.services.historical_service import historical_service

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()

# ── Performance Caches ──────────────────────────────────────────
_STOCK_MODEL_CACHE = {}      # {symbol: StockObject}
_CANDLE_PERSISTED_SET = set() # {(symbol, date)}


@shared_task(name="apps.market.tasks.fetch_and_broadcast")
def fetch_and_broadcast():
    """
    Main task — every 30 seconds.
    1. Holiday / Phase Check
    2. Stale Data Detection (Hashing)
    3. Signal Classification with baseline LTP + OI
    4. Signal transition logging (SignalLog)
    5. WebSocket broadcast
    """
    if not is_trading_day() or is_market_holiday():
        print("Market holiday or weekend — skipping fetch")
        logger.info("Market holiday or weekend — skipping fetch")
        return

    phase = get_market_phase()
    set_phase(phase)

    if phase == "CLOSED":
        print(f"Market phase is {phase} — skipping fetch")
        logger.info("Market closed — skipping fetch")
        return

    print(f"Current Market Phase: {phase}")

    # ── 1. Fetch data from API ────────────────────────────
    try:
        stocks = fetch_market_data()
        if not stocks:
            print("API returned NO stocks")
            return

        print(f"Fetched {len(stocks)} stocks from API/Mock")

        # Stale data check
        raw_json = json.dumps(stocks, sort_keys=True)
        new_hash = hashlib.md5(raw_json.encode()).hexdigest()
        old_hash = get_data_hash()

        if new_hash == old_hash:
            print("Stale data detected (hash match) — skipping broadcast")
            logger.info("Stale data detected (hash match) — skipping broadcast")
            return

        set_data_hash(new_hash)
    except Exception as e:
        logger.error(f"Data fetch/hash failed: {e}")
        return

    # ── 2. Process each stock ─────────────────────────────
    broadcast_payload = []
    snapshots_to_create = []
    signal_logs_to_create = []
    today = timezone.now().date()
    now_ts = timezone.now().isoformat()

    from apps.market.models import Stock, OISnapshot, SignalLog
    all_stocks_qs = Stock.objects.filter(symbol__in=[s["symbol"] for s in stocks])
    for s_obj in all_stocks_qs:
        _STOCK_MODEL_CACHE[s_obj.symbol] = s_obj

    for stock in stocks:
        symbol = stock["symbol"]
        register_symbol(symbol)
        set_stock(symbol, stock)

        candle = get_candle(symbol)

        # Lazy loading for late-entry stocks
        if not candle and phase in ("WATCH", "OPEN"):
            logger.info(f"Late entry detected for {symbol} — triggering lazy load")
            fetch_historical_candle_task.delay(symbol)

        # Candle building during 9:15-9:20
        if phase == "CANDLE":
            candle = update_candle(candle, stock["ltp"], stock["ltp"])
            set_candle(symbol, candle)

            # Store baseline LTP and OI during candle phase
            # (first tick becomes the baseline)
            if not get_baseline_ltp(symbol):
                set_baseline_ltp(symbol, stock["prev_close"])
            if not get_baseline_oi(symbol):
                set_baseline_oi(symbol, stock.get("oi", 0))

        # Self-healing: persist candle to DB
        if phase in ("WATCH", "OPEN") and candle:
            _ensure_candle_persisted(symbol, candle, stock, today)

        # ── Signal Classification ──
        baseline_ltp = get_baseline_ltp(symbol)
        baseline_oi  = get_baseline_oi(symbol)

        # Fallback: if baseline not set yet (e.g. joined late), use prev_close
        if baseline_ltp is None:
            baseline_ltp = stock["prev_close"]
            set_baseline_ltp(symbol, baseline_ltp)
        if baseline_oi is None:
            baseline_oi = stock.get("oi", 0)
            set_baseline_oi(symbol, baseline_oi)

        current_signal = get_signal(symbol)
        signal = classify_signal(
            stock, candle, phase,
            baseline_ltp=baseline_ltp,
            baseline_oi=baseline_oi,
            current_signal=current_signal,
        )

        # Timestamp new signals
        prev_signal_type = current_signal.get("signal", "NEUTRAL") if current_signal else "NEUTRAL"
        if signal["signal"] != prev_signal_type and signal["signal"] != "NEUTRAL":
            signal["signal_ts"] = now_ts
            # Log the transition
            stock_obj = _STOCK_MODEL_CACHE.get(symbol)
            if not stock_obj:
                stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)
                _STOCK_MODEL_CACHE[symbol] = stock_obj

            signal_logs_to_create.append(SignalLog(
                stock=stock_obj,
                signal_type=signal["signal"],
                ltp_at_signal=stock["ltp"],
                oi_at_signal=stock.get("oi", 0),
                baseline_ltp=baseline_ltp,
                baseline_oi=baseline_oi,
                candle_high=candle["high"] if candle else None,
                candle_low=candle["low"] if candle else None,
                reason=signal.get("reason", ""),
                date=today,
            ))

        set_signal(symbol, signal)

        # ── Prepare OI Snapshot ──
        stock_obj = _STOCK_MODEL_CACHE.get(symbol)
        if not stock_obj:
            stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)
            _STOCK_MODEL_CACHE[symbol] = stock_obj

        snapshots_to_create.append(OISnapshot(
            stock=stock_obj,
            date=today,
            prev_close=stock["prev_close"],
            ltp=stock["ltp"],
            open_price=candle["open"] if candle else stock["ltp"],
            high=candle["high"] if candle else stock["ltp"],
            low=candle["low"] if candle else stock["ltp"],
            oi_current=stock.get("oi", 0),
            oi_previous=stock.get("oi_prev", 0),
            oi_change=stock.get("oi_change", 0),
            volume=stock.get("volume", 0)
        ))

        broadcast_payload.append({
            "symbol":       symbol,
            "ltp":          stock["ltp"],
            "prev_close":   stock["prev_close"],
            "baseline_ltp": baseline_ltp,
            "baseline_oi":  baseline_oi,
            "oi":           stock.get("oi", 0),
            "oi_change":    stock.get("oi_change"),
            "volume":       stock.get("volume"),
            "candle":       candle,
            "signal":       signal,
        })

    # Bulk create snapshots and signal logs
    if snapshots_to_create:
        OISnapshot.objects.bulk_create(snapshots_to_create, ignore_conflicts=True)

    if signal_logs_to_create:
        SignalLog.objects.bulk_create(signal_logs_to_create)
        logger.info(f"Logged {len(signal_logs_to_create)} signal transitions")

    # ── 3. WebSocket broadcast ────────────────────────────
    if broadcast_payload:
        async_to_sync(channel_layer.group_send)(
            "market_data",
            {
                "type":    "market.update",
                "phase":   phase,
                "stocks":  broadcast_payload,
                "tick_at": now_ts,
            }
        )

    logger.info(f"Broadcast done | {len(broadcast_payload)} stocks")


# Deprecated
def _persist_snapshot(stock, candle, signal):
    pass


@shared_task(name="apps.market.tasks.fetch_historical_candle_task")
def fetch_historical_candle_task(symbol):
    """Async task to fetch missing 9:15 candle for late-entry stocks."""
    candle = historical_service.fetch_915_candle(symbol)
    if candle:
        set_candle(symbol, candle)
        logger.info(f"Successfully lazy-loaded 9:15 candle for {symbol}")


def _ensure_candle_persisted(symbol, candle, stock_data, today):
    """Helper to ensure candle is in DB even if 9:20 task failed."""
    if (symbol, today) in _CANDLE_PERSISTED_SET:
        return

    from apps.market.models import Stock, Candle5Min

    stock_obj = _STOCK_MODEL_CACHE.get(symbol)
    if not stock_obj:
        stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)
        _STOCK_MODEL_CACHE[symbol] = stock_obj

    if not Candle5Min.objects.filter(stock=stock_obj, date=today).exists():
        Candle5Min.objects.create(
            stock=stock_obj,
            date=today,
            open_price=candle["open"],
            high=candle["high"],
            low=candle["low"],
            close_price=candle["close"],
            prev_close=stock_data["prev_close"]
        )
        logger.info(f"Self-healing: Persisted 5-min candle for {symbol}")

    _CANDLE_PERSISTED_SET.add((symbol, today))


# ── Daily Maintenance Tasks ───────────────────────────────────────

@shared_task(name="apps.market.tasks.sync_daily_metadata")
def sync_daily_metadata():
    """Run at 9:01 AM — Fetch prev close + set baseline for all symbols."""
    from apps.market.models import Stock
    from apps.market.services.nse_service import nse_service

    raw_data = nse_service.fetch_oi_spurts()
    for item in raw_data:
        symbol = item.get("symbol")
        if symbol:
            Stock.objects.get_or_create(symbol=symbol)
            prev_close = float(item.get("underlyingValue", 0))
            set_prev_close(symbol, prev_close)
            # Set baseline LTP (9 AM reference = prev_close)
            set_baseline_ltp(symbol, prev_close)
            # Set baseline OI
            oi = int(item.get("latestOI", 0) or item.get("prevOI", 0) or 0)
            set_baseline_oi(symbol, oi)

    logger.info(f"Daily metadata + baseline sync completed for {len(raw_data)} symbols")
    print(f"Daily metadata + baseline sync completed for {len(raw_data)} symbols")


@shared_task(name="apps.market.tasks.cleanup_market_data")
def cleanup_market_data():
    """Run via Beat — Retention logic (30 days)."""
    from apps.market.models import OISnapshot, SignalLog
    cutoff = timezone.now() - timedelta(days=30)
    deleted_snaps, _ = OISnapshot.objects.filter(timestamp__lt=cutoff).delete()
    deleted_logs, _ = SignalLog.objects.filter(timestamp__lt=cutoff).delete()
    logger.info(f"Retention Cleanup: Deleted {deleted_snaps} snapshots, {deleted_logs} signal logs")


@shared_task(name="apps.market.tasks.reset_market_state")
def reset_market_state():
    """Run at 9:00 AM — Fresh slate for Redis."""
    clear_market_state()
    set_data_hash("")
    logger.info("Market state reset for new day")