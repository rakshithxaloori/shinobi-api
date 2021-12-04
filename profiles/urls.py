from django.urls import path

from profiles import views

urlpatterns = [
    path("trending/", views.trending_profiles_view, name="trending profiles"),
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
    path(
        "followers/<str:username>/<int:begin_index>/<int:end_index>/",
        views.followers_list_view,
        name="followers",
    ),
    path(
        "following/<str:username>/<int:begin_index>/<int:end_index>/",
        views.following_list_view,
        name="following",
    ),
    path("games/search/", views.search_games_view, name="serch games"),
    path("games/get/", views.get_games_view, name="get games"),
    path("games/remove/", views.remove_game_view, name="add game"),
    path("games/add/", views.add_game_view, name="remove game"),
]
