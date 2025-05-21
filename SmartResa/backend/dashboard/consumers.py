# dashboard/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Seat

class SeatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.channel_layer.group_add("seats", self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("seats", self.channel_name)

    async def seat_update(self, event):
        await self.send(text_data=json.dumps(event))
# dashboard/consumers.py
class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_add(
                f"notifications_{user.id}",
                self.channel_name
            )
            await self.accept()

    async def disconnect(self, close_code):
        user = self.scope["user"]
        if user.is_authenticated:
            await self.channel_layer.group_discard(
                f"notifications_{user.id}",
                self.channel_name
            )

    async def send_notification(self, event):
        await self.send(text_data=json.dumps(event["content"]))