from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .models import AlertRule, AlertLog
from .serializers import AlertRuleSerializer, AlertLogSerializer


class AlertRuleListCreateView(APIView):
    """
    GET  /api/alerts/rules/   → apne saare rules
    POST /api/alerts/rules/   → naya rule banao
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        rules = AlertRule.objects.filter(user=request.user).select_related("stock")
        return Response(AlertRuleSerializer(rules, many=True).data)

    def post(self, request):
        serializer = AlertRuleSerializer(data=request.data, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class AlertRuleDetailView(APIView):
    """
    GET    /api/alerts/rules/<id>/  → detail
    PUT    /api/alerts/rules/<id>/  → update
    DELETE /api/alerts/rules/<id>/  → delete
    """
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return AlertRule.objects.get(pk=pk, user=user)
        except AlertRule.DoesNotExist:
            return None

    def get(self, request, pk):
        rule = self.get_object(pk, request.user)
        if not rule:
            return Response({"error": "Not found"}, status=404)
        return Response(AlertRuleSerializer(rule).data)

    def put(self, request, pk):
        rule = self.get_object(pk, request.user)
        if not rule:
            return Response({"error": "Not found"}, status=404)
        serializer = AlertRuleSerializer(rule, data=request.data, partial=True, context={"request": request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def delete(self, request, pk):
        rule = self.get_object(pk, request.user)
        if not rule:
            return Response({"error": "Not found"}, status=404)
        rule.delete()
        return Response(status=204)


class AlertLogView(APIView):
    """
    GET /api/alerts/logs/   → apne saare sent alerts
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        logs = (
            AlertLog.objects
            .filter(user=request.user)
            .select_related("stock")
            .order_by("-sent_at")[:50]
        )
        return Response(AlertLogSerializer(logs, many=True).data)


class ToggleAlertRuleView(APIView):
    """
    POST /api/alerts/rules/<id>/toggle/   → on/off karo
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            rule = AlertRule.objects.get(pk=pk, user=request.user)
            rule.is_active = not rule.is_active
            rule.save(update_fields=["is_active"])
            return Response({"is_active": rule.is_active})
        except AlertRule.DoesNotExist:
            return Response({"error": "Not found"}, status=404)