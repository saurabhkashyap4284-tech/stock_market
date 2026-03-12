from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count

from .models import SignalEvent
from .serializers import SignalEventSerializer


class SignalHistoryView(APIView):
    """
    GET /api/signals/history/
    Query params:
      - date     (default: today)
      - symbol   (optional filter)
      - signal   (optional: BEARISH, BULLISH, etc.)
      - strength (optional: STRONG, MODERATE)
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date     = request.query_params.get("date", str(timezone.now().date()))
        symbol   = request.query_params.get("symbol", "").upper()
        signal   = request.query_params.get("signal", "").upper()
        strength = request.query_params.get("strength", "").upper()

        qs = SignalEvent.objects.select_related("stock").filter(date=date)

        if symbol:
            qs = qs.filter(stock__symbol=symbol)
        if signal:
            qs = qs.filter(signal_type=signal)
        if strength:
            qs = qs.filter(strength=strength)

        qs = qs.order_by("-created_at")[:200]
        return Response(SignalEventSerializer(qs, many=True).data)


class SignalSummaryView(APIView):
    """
    GET /api/signals/summary/?date=2026-03-09
    Ek din ka signal count summary.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        date = request.query_params.get("date", str(timezone.now().date()))

        summary = (
            SignalEvent.objects
            .filter(date=date)
            .values("signal_type", "strength")
            .annotate(count=Count("id"))
            .order_by("signal_type")
        )

        return Response({
            "date":    date,
            "summary": list(summary),
            "total":   SignalEvent.objects.filter(date=date).count(),
        })


class StockSignalTimelineView(APIView):
    """
    GET /api/signals/timeline/<symbol>/?date=2026-03-09
    Ek stock ke din bhar ke signals timeline.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, symbol):
        date = request.query_params.get("date", str(timezone.now().date()))
        qs   = (
            SignalEvent.objects
            .filter(stock__symbol=symbol.upper(), date=date)
            .order_by("created_at")
        )
        return Response(SignalEventSerializer(qs, many=True).data)