from django.urls import path

from feed import views

urlpatterns = [
    path("posts/following/", views.following_feed_view, name="feed"),
    path(
        "posts/world/",
        views.world_feed_view,
        name="world posts",
    ),
    path("posts/profile/", views.get_profile_posts_view, name="my posts"),
    path("post/", views.get_post_view, name="get post"),
    path("post/delete/", views.delete_post_view, name="delete post"),
    path("post/like/", views.like_post_view, name="like post"),
    path("post/unlike/", views.unlike_post_view, name="unlike post"),
    path("post/share/", views.share_post_view, name="share post"),
    path("post/report/", views.report_post_view, name="report post"),
    path("post/repost/", views.repost_view, name="repost"),
]
