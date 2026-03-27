# Market app URLs
from django.urls import path
from . import views

urlpatterns = [
    path("live/",              views.LiveSnapshotView.as_view(),    name="live-snapshot"),
    path("live/<str:symbol>/", views.LiveStockDetailView.as_view(), name="live-stock-detail"),
    path("stocks/",            views.StockListView.as_view(),       name="stock-list"),
    path("oi-history/",        views.OIHistoryView.as_view(),       name="oi-history"),
    path("candles/",           views.Candle5MinView.as_view(),      name="candles-5min"),
    path("phase/",             views.MarketPhaseView.as_view(),     name="market-phase"),
    path("signal-logs/",       views.SignalLogView.as_view(),       name="signal-logs"),
    path("signal-logs/download/", views.SignalLogDownloadCSVView.as_view(), name="signal-logs-download"),
    path("purge/",             views.DataPurgeView.as_view(),       name="purge-data"),
    path("clear-state/",       views.ClearMarketStateView.as_view(),name="clear-state"),
]