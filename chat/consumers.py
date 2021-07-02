import json

from django.core.serializers.json import DjangoJSONEncoder

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer

from authentication.models import User
from chat.models import Chat, Message


class ChatRoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["chat_id"]
        self.room_chat_name = "chat_%s" % self.room_name

        await self.channel_layer.group_add(self.room_chat_name, self.channel_name)

        await self.accept()

        # await self.channel_layer.group_send(
        #     self.room_chat_name,
        #     {"type": "send.message", "message": "Hello there!", "sent_by": "API"},
        # )

    async def disconnect(self, code):
        if code == 4200:
            # TODO Someone tried to do something that they don't
            # have access to
            print("Someone tried to do something that they don't have access to")

        await self.channel_layer.group_discard(self.room_chat_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json.get("message", None)
        username = text_data_json.get("username", None)

        new_message = await self.create_message(message, username)
        if new_message is None:
            await self.close(4200)
        else:
            await self.channel_layer.group_send(
                self.room_chat_name,
                {"type": "send.message", "message": new_message},
            )

    async def send_message(self, event):
        message = event.get("message", None)
        # This method sends the "send.message" type dispatch events
        await self.send(
            text_data=json.dumps(
                {
                    "message": message.get("message", None),
                    "sent_at": message.get("sent_at", None),
                    "sent_by": message.get("sent_by", None),
                },
                cls=DjangoJSONEncoder,
            )
        )

    @database_sync_to_async
    def create_message(self, message, username):
        # Create message instance
        try:
            sent_by_user = User.objects.get(username=username)
            chat = Chat.objects.get(id=self.room_name)

            if sent_by_user not in chat.users.all():
                return None

            else:
                new_message = Message.objects.create(
                    chat=chat,
                    sent_by=sent_by_user,
                    text=message,
                )

                return {
                    "message": new_message.text,
                    "sent_at": new_message.sent_at,
                    "sent_by": new_message.sent_by.username,
                }

        except (User.DoesNotExist, Chat.DoesNotExist):
            return None
