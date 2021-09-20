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
        if self.scope["user"].is_anonymous:
            self.close(4200)
            return

        self.user = self.scope["user"]

        chat_access = await self.check_chat_access()
        if chat_access is False:
            self.close(4200)
            return

        await self.channel_layer.group_add(self.room_chat_name, self.channel_name)

        await self.accept()

        # await self.channel_layer.group_send(
        #     self.room_chat_name,
        #     {"type": "send.message", "message": "Hello there!", "sent_by": "API"},
        # )

    async def disconnect(self, code):
        if code == 4200:
            # Someone tried to do something that they don't
            # have access to
            print("Someone tried to do something that they don't have access to")

        await self.channel_layer.group_discard(self.room_chat_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        print("consumers.receive text_data_json", text_data_json)
        message = text_data_json.get("message", None)

        new_message = await self.create_message(message)
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
                message,
                cls=DjangoJSONEncoder,
            )
        )

    @database_sync_to_async
    def check_chat_access(
        self,
    ):
        # Check if the user has access to the chat
        try:
            chat = Chat.objects.get(id=self.room_name)
            return self.user in chat.users.all()
        except Chat.DoesNotExist:
            return False

    @database_sync_to_async
    def create_message(self, message):
        # Create message instance
        try:
            chat = Chat.objects.get(id=self.room_name)

            if self.user not in chat.users.all():
                return None

            else:
                new_message = Message.objects.create(
                    chat=chat,
                    sent_by=self.user,
                    text=message,
                )

                chat.last_updated = new_message.sent_at
                chat.save(update_fields=["last_updated"])

                return {
                    "text": new_message.text,
                    "sent_at": new_message.sent_at,
                    "sent_by": {
                        "username": new_message.sent_by.username,
                        "picture": new_message.sent_by.picture,
                    },
                }

        except (User.DoesNotExist, Chat.DoesNotExist):
            return None
