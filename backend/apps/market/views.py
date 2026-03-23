# REST endpoints
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from django.utils import timezone

from .models import Stock, OISnapshot, Candle5Min, SignalLog
from .serializers import (
    StockSerializer, OISnapshotSerializer,
    Candle5MinSerializer, LiveStockSerializer,
    SignalLogSerializer,
)
from utils.redis_client import (
    get_all_symbols, get_stock, get_candle,
    get_signal, get_phase, clear_market_state
)


class LiveSnapshotView(APIView):
    """
    GET /api/market/live/
    Redis se current live data — saare stocks.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        symbols  = get_all_symbols()
        phase    = get_phase()
        result   = []

        # Watchlist filter optional
        watchlist = request.query_params.get("watchlist")
        if watchlist:
            symbols = [s for s in symbols if s in watchlist.upper().split(",")]

        for symbol in sorted(symbols):
            stock  = get_stock(symbol)
            if not stock:
                continue
            stock["symbol"] = symbol
            stock["candle"] = get_candle(symbol)
            stock["signal"] = get_signal(symbol)
            result.append(stock)

        return Response({
            "phase":  phase,
            "count":  len(result),
            "stocks": result,
        })


class LiveStockDetailView(APIView):
    """
    GET /api/market/live/<symbol>/
    Ek stock ki live detail.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, symbol):
        symbol = symbol.upper()
        stock  = get_stock(symbol)
        if not stock:
            return Response({"error": f"{symbol} not found in live data"}, status=404)

        return Response({
            "symbol": symbol,
            "phase":  get_phase(),
            "data":   stock,
            "candle": get_candle(symbol),
            "signal": get_signal(symbol),
        })


class StockListView(APIView):
    """
    GET /api/market/stocks/         → all stocks
    POST /api/market/stocks/        → add new stock
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        qs = Stock.objects.filter(is_active=True)
        return Response(StockSerializer(qs, many=True).data)

    def post(self, request):
        serializer = StockSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class OIHistoryView(APIView):
    """
    GET /api/market/oi-history/?symbol=RELIANCE&date=2026-03-09
    Ek stock ke OI snapshots — historical data.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        symbol = request.query_params.get("symbol", "").upper()
        date   = request.query_params.get("date", timezone.now().date())

        qs = OISnapshot.objects.select_related("stock")
        if symbol:
            qs = qs.filter(stock__symbol=symbol)
        if date:
            qs = qs.filter(date=date)

        qs = qs.order_by("-timestamp")[:100]
        return Response(OISnapshotSerializer(qs, many=True).data)


class Candle5MinView(APIView):
    """
    GET /api/market/candles/?date=2026-03-09
    Saare stocks ke 5-min candles ek date ke liye.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.query_params.get("date", str(timezone.now().date()))
        qs   = Candle5Min.objects.filter(date=date).select_related("stock")

        signal_filter = request.query_params.get("signal")
        if signal_filter == "bearish":
            qs = qs.filter(all_below_prev_close=True)
        elif signal_filter == "bullish":
            qs = qs.filter(all_above_prev_close=True)

        return Response(Candle5MinSerializer(qs, many=True).data)


class MarketPhaseView(APIView):
    """
    GET /api/market/phase/
    Current market phase.
    """
    permission_classes = [AllowAny]

    def get(self, request):
        from apps.market.services.phase_detector import get_market_phase
        phase = get_market_phase()
        return Response({"phase": phase, "time": timezone.now().isoformat()})


class DataPurgeView(APIView):
    """
    POST /api/market/purge/
    Manually clean historical OISnapshots.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Allow specifying 'days' to keep, default 0 (clean all)
        days = int(request.data.get("days", 0))
        if days == 0:
            deleted, _ = OISnapshot.objects.all().delete()
        else:
            cutoff = timezone.now() - timezone.timedelta(days=days)
            deleted, _ = OISnapshot.objects.filter(timestamp__lt=cutoff).delete()
            
        return Response({
            "message": f"Successfully deleted {deleted} records.",
            "deleted_count": deleted
        })


class SignalLogView(APIView):
    """
    GET /api/market/signal-logs/?type=BEARISH&date=2026-03-21
    KPI drilldown — click Bearish card → see all bearish stocks with timestamps.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        signal_type = request.query_params.get("type", "").upper()
        date = request.query_params.get("date", str(timezone.now().date()))

        qs = SignalLog.objects.select_related("stock").filter(date=date)

        if signal_type:
            # Support "FALSE_ALERTS" as a combined filter
            if signal_type == "FALSE_ALERTS":
                qs = qs.filter(signal_type__in=["FALSE_ALERT_BULL", "FALSE_ALERT_BEAR"])
            else:
                qs = qs.filter(signal_type=signal_type)

        qs = qs.order_by("-timestamp")[:200]
        return Response(SignalLogSerializer(qs, many=True).data)


class ClearMarketStateView(APIView):
    """
    POST /api/market/clear-state/
    Manually clear Redis state (candles, signals, etc).
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        clear_market_state()
        return Response({"message": "Market state cleared successfully."})