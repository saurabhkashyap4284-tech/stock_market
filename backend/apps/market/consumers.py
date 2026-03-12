import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async


class MarketConsumer(AsyncWebsocketConsumer):
    """
    Frontend WebSocket se connect hota hai yahan.
    Celery task broadcast karta hai → ye consumer frontend ko push karta hai.
    """

    GROUP = "market_data"

    async def connect(self):
        # User auth check
        user = self.scope.get("user")
        if not user or not user.is_authenticated:
            await self.close(code=4001)
            return

        # Group join karo
        await self.channel_layer.group_add(self.GROUP, self.channel_name)
        await self.accept()

        # Connect hone pe current state bhejo
        await self.send_initial_state()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.GROUP, self.channel_name)

    async def receive(self, text_data):
        """
        Frontend se message aa sakta hai — watchlist filter etc.
        """
        try:
            data = json.loads(text_data)
            action = data.get("action")

            if action == "ping":
                await self.send(json.dumps({"type": "pong"}))

            elif action == "get_snapshot":
                await self.send_initial_state()

        except Exception as e:
            await self.send(json.dumps({"type": "error", "message": str(e)}))

    async def market_update(self, event):
        """
        Celery task se broadcast aata hai — frontend ko forward karo.
        Event type: 'market.update' → 'market_update' (channels convention)
        """
        await self.send(json.dumps({
            "type":    "market_update",
            "phase":   event["phase"],
            "stocks":  event["stocks"],
            "tick_at": event["tick_at"],
        }))

    async def send_initial_state(self):
        """Naya connect hua user — Redis se current snapshot bhejo."""
        from utils.redis_client import get_all_symbols, get_stock, get_candle, get_signal, get_phase

        symbols = await database_sync_to_async(get_all_symbols)()
        phase   = await database_sync_to_async(get_phase)()

        stocks = []
        for symbol in symbols:
            stock  = await database_sync_to_async(get_stock)(symbol)
            candle = await database_sync_to_async(get_candle)(symbol)
            signal = await database_sync_to_async(get_signal)(symbol)
            if stock:
                stocks.append({
                    "symbol": symbol,
                    **stock,
                    "candle": candle,
                    "signal": signal,
                })

        await self.send(json.dumps({
            "type":   "initial_state",
            "phase":  phase,
            "stocks": stocks,
        }))