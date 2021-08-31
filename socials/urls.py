from django.urls import path

from socials import views

urlpatterns = [
    path("status/", views.socials_status_view, name="socials status"),
    path("instagram/connect/", views.instagram_connect_view, name="instagram connect"),
    path(
        "instagram/disconnect/",
        views.instagram_disconnect_view,
        name="instagram disconnect",
    ),
    path("twitch/connect/", views.twitch_connect_view, name="twitch connect"),
    path("twitch/callback/", views.twitch_callback_view, name="twitch callback"),
    path("twitch/disconnect/", views.twitch_disconnect_view, name="twitch disconnect"),
    path("youtube/connect/", views.youtube_connect_view, name="youtube connect"),
    path(
        "youtube/select/",
        views.youtube_select_channel_view,
        name="youtube channel select",
    ),
    path(
        "youtube/disconnect/", views.youtube_disconnect_view, name="youtube disconnect"
    ),
]
