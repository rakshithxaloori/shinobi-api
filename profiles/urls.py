from django.urls import path

from profiles import views

urlpatterns = [
    path("all/", views.all_profiles_view, name="all profiles"),
    path("", views.my_profile_view, name="my profile"),
    path("<str:username>/", views.profile_view, name="profile"),
    path("follow/<str:username>/", views.follow_user_view, name="follow user"),
    path("unfollow/<str:username>/", views.unfollow_user_view, name="unfollow user"),
    path(
        "remove_follower/<str:username>/",
        views.remove_follower_view,
        name="remove follower",
    ),
    path("connect/twitch/", views.twitch_connect_view, name="twitch connect"),
    path("connect/youtube/", views.youtube_connect_view, name="youtube connect"),
    path(
        "connect/youtube/select/",
        views.youtube_select_channel_view,
        name="youtube connect select",
    ),
]
