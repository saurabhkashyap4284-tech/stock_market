# Signal log URLs
from django.urls import path
from . import views

urlpatterns = [
    path("history/",                       views.SignalHistoryView.as_view(),       name="signal-history"),
    path("summary/",                       views.SignalSummaryView.as_view(),       name="signal-summary"),
    path("timeline/<str:symbol>/",         views.StockSignalTimelineView.as_view(), name="signal-timeline"),
]