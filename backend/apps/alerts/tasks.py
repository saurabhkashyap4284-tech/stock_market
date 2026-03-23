# Celery tasks - send email/notification
import logging
from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)


@shared_task(name="apps.alerts.tasks.check_and_fire_alerts")
def check_and_fire_alerts():
    """
    Har 30 sec chalti hai.
    Active alert rules check karo — match hone pe email bhejo.
    """
    from apps.alerts.models import AlertRule, AlertLog
    from utils.redis_client import get_all_symbols, get_signal, get_stock

    active_rules = AlertRule.objects.filter(is_active=True).select_related("user", "stock")

    symbols = get_all_symbols()

    for symbol in symbols:
        signal = get_signal(symbol)
        if not signal or signal["signal"] == "NEUTRAL":
            continue

        stock_data = get_stock(symbol)
        if not stock_data:
            continue

        # Is symbol ke liye matching rules dhundo
        for rule in active_rules:
            # Stock filter
            if rule.stock and rule.stock.symbol != symbol:
                continue

            # Signal type match
            if rule.signal_type != "ANY" and rule.signal_type != signal["signal"]:
                continue

            # Strength filter
            if rule.only_strong and signal["strength"] != "STRONG":
                continue

            # Already sent in last 5 min? Skip
            from django.utils import timezone
            from datetime import timedelta
            recent = AlertLog.objects.filter(
                user=rule.user,
                stock__symbol=symbol,
                signal_type=signal["signal"],
                sent_at__gte=timezone.now() - timedelta(minutes=5)
            ).exists()

            if recent:
                continue

            # ── Send alert ────────────────────────────────
            from apps.market.models import Stock
            stock_obj, _ = Stock.objects.get_or_create(symbol=symbol)

            log = AlertLog.objects.create(
                user        = rule.user,
                rule        = rule,
                stock       = stock_obj,
                signal_type = signal["signal"],
                strength    = signal["strength"],
                ltp         = stock_data["ltp"],
            )

            if rule.via_email:
                send_alert_email.delay(log.id)


@shared_task(name="apps.alerts.tasks.send_alert_email")
def send_alert_email(log_id: int):
    """Email bhejo — alag task mein taaki main loop block na ho."""
    from apps.alerts.models import AlertLog

    try:
        log = AlertLog.objects.select_related("user", "stock").get(id=log_id)

        subject = f"🚨 F&O Alert: {log.stock.symbol} — {log.signal_type}"
        message = f"""
Namaskar {log.user.get_full_name() or log.user.email},

Aapka alert trigger hua hai:

Stock     : {log.stock.symbol}
Signal    : {log.signal_type} ({log.strength})
LTP       : ₹{log.ltp:,.2f}
Time      : {log.sent_at.strftime('%d %b %Y, %I:%M %p IST')}

F&O Monitor pe dekhen: http://localhost:5173

— FO Monitor
        """.strip()

        send_mail(
            subject      = subject,
            message      = message,
            from_email   = settings.EMAIL_HOST_USER,
            recipient_list=[log.user.email],
            fail_silently= False,
        )

        log.delivered = True
        log.save(update_fields=["delivered"])
        logger.info(f"Alert email sent to {log.user.email} for {log.stock.symbol}")

    except Exception as e:
        logger.error(f"Alert email failed for log {log_id}: {e}")