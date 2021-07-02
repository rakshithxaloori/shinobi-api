from django.urls import path

from chat import views

urlpatterns = [
    path("", views.chats_view, name="my chats"),
    path(
        "messages/<str:chat_id>/<int:begin_index>/<int:end_index>/",
        views.chat_messages,
        name="chat messages",
    ),
]
