# Alerts URLs
from django.urls import path
from . import views

urlpatterns = [
    path("rules/",               views.AlertRuleListCreateView.as_view(), name="alert-rules"),
    path("rules/<int:pk>/",      views.AlertRuleDetailView.as_view(),     name="alert-rule-detail"),
    path("rules/<int:pk>/toggle/",views.ToggleAlertRuleView.as_view(),    name="alert-rule-toggle"),
    path("logs/",                views.AlertLogView.as_view(),            name="alert-logs"),
]