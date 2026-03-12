from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path("admin/",         admin.site.urls),

    # JWT auth
    path("api/auth/login/",   TokenObtainPairView.as_view(),  name="token_obtain"),
    path("api/auth/refresh/", TokenRefreshView.as_view(),     name="token_refresh"),

    # Apps
    path("api/users/",    include("apps.users.urls")),
    path("api/market/",   include("apps.market.urls")),
    path("api/signals/",  include("apps.signals_log.urls")),
    path("api/alerts/",   include("apps.alerts.urls")),
]