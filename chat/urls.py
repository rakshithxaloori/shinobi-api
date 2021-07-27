from django.urls import path

from chat import views

urlpatterns = [
    path(
        "messages/<str:chat_id>/<int:begin_index>/<int:end_index>/",
        views.chat_messages,
        name="chat messages",
    ),
    path("read/", views.last_read_view, name="last read"),
    path("<int:begin_index>/<int:end_index>/", views.chats_view, name="my chats"),
]
