from django.urls import path

from clips import views

urlpatterns = [
    path("check/", views.upload_check_view, name="upload check"),
    path(
        "presigned/web/",
        views.generate_s3_presigned_url_view,
        name="presigned post url",
    ),
    path(
        "presigned/mobile/",
        views.generate_s3_presigned_url_view,
        name="presigned post url",
    ),
    path("success/", views.upload_successful_view, name="check success upload"),
    path("viewed/", views.viewed_clip_view, name="viewed clip"),
    path(
        "mediaconvert/callback/", views.mediaconvert_sns_view, name="mediaconvert sns"
    ),
]
