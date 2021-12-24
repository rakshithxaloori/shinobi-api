from django.urls import path

from feed import views

urlpatterns = [
    path("following/", views.following_feed_view, name="feed"),
    path(
        "world/",
        views.world_feed_view,
        name="world posts",
    ),
    path("posts/profile/", views.get_profile_posts_view, name="my posts"),
    path("post/", views.get_post_view, name="get post"),
    path("delete/", views.delete_post_view, name="delete post"),
    path("like/", views.like_post_view, name="like post"),
    path("unlike/", views.unlike_post_view, name="unlike post"),
    path("share/", views.share_post_view, name="share post"),
    path("report/", views.report_post_view, name="report post"),
]
