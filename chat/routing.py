from django.urls import re_path

from chat.consumers import ChatRoomConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<chat_id>[\w\-\.]+)/$", ChatRoomConsumer.as_asgi())
]
