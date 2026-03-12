import logging
from celery import shared_task
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.utils import timezone

from utils.redis_client import (
    set_stock, get_stock, set_candle, get_candle,
    set_signal, get_signal, set_phase, get_phase,
    register_symbol, get_all_symbols
)
from apps.market.services.phase_detector import get_market_phase, is_trading_day
from apps.market.services.signal_engine import classify_signal
from apps.market.services.data_fetcher import fetch_market_data
from apps.market.services.candle_builder import update_candle

logger = logging.getLogger(__name__)
channel_layer = get_channel_layer()


@shared_task(name="apps.market.tasks.fetch_and_broadcast")
def fetch_and_broadcast():
    """
    Main task — har 30 seconds chalti hai.
    1. Market data fetch karo
    2. Redis mein save karo
    3. WebSocket se frontend ko push karo
    """
    if not is_trading_day():
        logger.info("Weekend hai — skipping fetch")
        return

    phase = get_market_phase()
    set_phase(phase)

    if phase == "CLOSED":
        logger.info("Market closed — skipping fetch")
        return

    logger.info(f"Fetching market data | Phase: {phase}")

    # ── 1. API se data fetch karo ─────────────────────────
    try:
        stocks = fetch_market_data()   # list of dicts
    except Exception as e:
        logger.error(f"Data fetch failed: {e}")
        return

    # ── 2. Process each stock ─────────────────────────────
    broadcast_payload = []

    for stock in stocks:
        symbol = stock["symbol"]
        register_symbol(symbol)

        # Redis mein latest tick save karo
        set_stock(symbol, stock)

        # CANDLE phase mein 5-min candle update karo
        if phase == "CANDLE":
            prev = get_candle(symbol) or {}
            updated_candle = update_candle(prev, stock["ltp"], stock["open"])
            set_candle(symbol, updated_candle)

        # Signal compute karo
        candle = get_candle(symbol)
        signal = classify_signal(stock, candle, phase)
        set_signal(symbol, signal)

        # Broadcast payload banao
        broadcast_payload.append({
            "symbol":    symbol,
            "ltp":       stock["ltp"],
            "prev_close":stock["prev_close"],
            "open":      stock.get("open"),
            "high":      stock.get("high"),
            "low":       stock.get("low"),
            "oi_change": stock.get("oi_change"),
            "volume":    stock.get("volume"),
            "candle":    candle,
            "signal":    signal,
        })

    # ── 3. WebSocket broadcast ────────────────────────────
    async_to_sync(channel_layer.group_send)(
        "market_data",
        {
            "type":    "market.update",
            "phase":   phase,
            "stocks":  broadcast_payload,
            "tick_at": timezone.now().isoformat(),
        }
    )

    logger.info(f"Broadcast done | {len(broadcast_payload)} stocks | Phase: {phase}")


@shared_task(name="apps.market.tasks.build_5min_candle")
def build_5min_candle():
    """
    9:20 AM pe chalti hai — 5-min candle DB mein save karo.
    Redis mein jo candle bani hai use PostgreSQL mein persist karo.
    """
    from apps.market.models import Stock, Candle5Min
    from django.utils import timezone

    today = timezone.now().date()
    symbols = get_all_symbols()
    saved = 0

    for symbol in symbols:
        candle = get_candle(symbol)
        stock_data = get_stock(symbol)

        if not candle or not stock_data:
            continue

        try:
            stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)
            Candle5Min.objects.update_or_create(
                stock=stock_obj,
                date=today,
                defaults={
                    "open_price":  candle["open"],
                    "high":        candle["high"],
                    "low":         candle["low"],
                    "close_price": candle["close"],
                    "prev_close":  stock_data["prev_close"],
                }
            )
            saved += 1
        except Exception as e:
            logger.error(f"Candle save failed for {symbol}: {e}")

    logger.info(f"5-min candles saved to DB: {saved}")


@shared_task(name="apps.market.tasks.run_signal_engine")
def run_signal_engine():
    """
    WATCH phase (9:20-9:30) mein signal events DB mein log karo.
    Ye alag task hai taaki signal history track ho sake.
    """
    from apps.signals_log.models import SignalEvent
    from apps.market.models import Stock
    from django.utils import timezone

    phase = get_phase()
    if phase not in ("WATCH", "OPEN"):
        return

    today = timezone.now().date()
    symbols = get_all_symbols()

    for symbol in symbols:
        signal = get_signal(symbol)
        if not signal or signal["signal"] == "NEUTRAL":
            continue

        stock_data = get_stock(symbol)
        if not stock_data:
            continue

        try:
            stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)

            # Duplicate avoid karo — same signal same minute mein dobara mat save karo
            last = SignalEvent.objects.filter(
                stock=stock_obj,
                date=today,
                signal_type=signal["signal"],
            ).order_by("-created_at").first()

            now = timezone.now()
            if last and (now - last.created_at).seconds < 60:
                continue   # 1 min ke andar same signal — skip

            SignalEvent.objects.create(
                stock      = stock_obj,
                date       = today,
                signal_type= signal["signal"],
                strength   = signal["strength"],
                reason     = signal["reason"],
                ltp        = stock_data["ltp"],
                phase      = phase,
            )
        except Exception as e:
            logger.error(f"Signal log failed for {symbol}: {e}")