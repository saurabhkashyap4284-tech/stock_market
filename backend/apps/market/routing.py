from django.urls import re_path
from apps.market.consumers import MarketConsumer

websocket_urlpatterns = [
    # Frontend connect karega: ws://localhost:8000/ws/market/
    re_path(r"^ws/market/$", MarketConsumer.as_asgi()),
]