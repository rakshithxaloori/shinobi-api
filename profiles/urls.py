from django.urls import path

from profiles import views

urlpatterns = [
    path("all/", views.all_profiles_view, name="all profiles"),
    path("my/", views.my_profile_view, name="my profile"),
    path("update/", views.update_profile_view, name="update profile"),
    path("u/<str:username>/", views.profile_view, name="profile"),
    path("search/<str:username>/", views.search_view, name="search"),
    path("follow/<str:username>/", views.follow_user_view, name="follow user"),
    path("unfollow/<str:username>/", views.unfollow_user_view, name="unfollow user"),
    path(
        "remove_follower/<str:username>/",
        views.remove_follower_view,
        name="remove follower",
    ),
    path("twitch/connect/", views.twitch_connect_view, name="twitch connect"),
    path("twitch/callback/", views.twitch_callback_view, name="twitch callback"),
    path("youtube/connect/", views.youtube_connect_view, name="youtube connect"),
    path(
        "youtube/select/",
        views.youtube_select_channel_view,
        name="youtube connect select",
    ),
]
