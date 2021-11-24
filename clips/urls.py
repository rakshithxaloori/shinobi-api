from django.urls import path

from clips import views

urlpatterns = [
    path("check/", views.upload_check_view, name="upload check"),
    path("presigned/", views.generate_s3_presigned_url_view, name="presigned post url"),
    path("success/", views.upload_successful_view, name="check success upload"),
    path("clips/all/", views.get_all_clips_view, name="all clips"),
    path("clips/profile/", views.get_profile_clips_view, name="my clips"),
    path("delete/", views.delete_clip_view, name="delete clip"),
    path("like/", views.like_clip_view, name="like clip"),
    path("unlike/", views.unlike_clip_view, name="unlike clip"),
    path("share/", views.share_clip_view, name="share clip"),
    path("report/", views.report_clip_view, name="report clip"),
]
