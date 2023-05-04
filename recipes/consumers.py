import json
import logging

from channels.generic.websocket import AsyncJsonWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class RealtimeConsumer(AsyncJsonWebsocketConsumer):
    group_name = "realtime"

    async def connect(self):
        assert self.channel_layer is not None
        await self.channel_layer.group_add(self.group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive_json(self, content: dict, **kwargs):
        logging.info("Socket received: ", content)
        pass

    @classmethod
    async def encode_json(cls, content):
        return json.dumps(content, default=str)

    async def raw_data(self, event):
        await self.send_json(event["message"])

    @classmethod
    def send_raw_data(cls, data: dict):
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(cls.group_name, {"type": "raw_data", "message": data})
