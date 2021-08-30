from django.urls import path

from socials import views

urlpatterns = [
    path("twitch/connect/", views.twitch_connect_view, name="twitch connect"),
    path("twitch/callback/", views.twitch_callback_view, name="twitch callback"),
    path("youtube/connect/", views.youtube_connect_view, name="youtube connect"),
    path(
        "youtube/select/",
        views.youtube_select_channel_view,
        name="youtube channel select",
    ),
]
