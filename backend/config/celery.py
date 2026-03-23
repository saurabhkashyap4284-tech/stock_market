import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.base")

app = Celery("fo_monitor")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# ── Periodic tasks ────────────────────────────────────────────────
app.conf.beat_schedule = {

    # Fetch market data every 30 seconds (during market hours)
    "fetch-market-data-30s": {
        "task":     "apps.market.tasks.fetch_and_broadcast",
        "schedule": 30.0,
    },

    # 1. Reset Redis at 9:00 AM
    "reset-market-state-900": {
        "task":     "apps.market.tasks.reset_market_state",
        "schedule": crontab(hour=9, minute=0),
    },

    # 2. Sync Metadata at 9:01 AM
    "sync-metadata-901": {
        "task":     "apps.market.tasks.sync_daily_metadata",
        "schedule": crontab(hour=9, minute=1),
    },

    # Build 5-min candle snapshot at 9:20 AM
    "build-5min-candle": {
        "task":     "apps.market.tasks.build_5min_candle",
        "schedule": crontab(hour=9, minute=20),
    },

    # Run signal engine every 30s during watch window (9:20–9:30)
    "run-signal-engine-30s": {
        "task":     "apps.market.tasks.run_signal_engine",
        "schedule": 30.0,
    },

    # Check alert rules every 30 seconds
    "check-alerts-30s": {
        "task":     "apps.alerts.tasks.check_and_fire_alerts",
        "schedule": 30.0,
    },
}