import json

from channels.generic.websocket import AsyncWebsocketConsumer


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["username"]
        self.room_chat_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_chat_name, self.channel_name)

        await self.accept()

        await self.channel_layer.group_send(
            self.room_chat_name, {"type": "send.message", "message": "Hello there!"}
        )

    async def disconnect(self, code):
        await self.channel_layer.group_discard(self.room_chat_name, self.chann)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        await self.channel_layer.group_send(
            self.room_chat_name, {"type": "send.message", "message": message}
        )

    async def send_message(self, event):
        message = event["message"]

        await self.send(text_data=json.dumps({"message": message}))
