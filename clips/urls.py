from django.urls import path

from clips import views

urlpatterns = [
    path("check/", views.upload_check_view, name="upload check"),
    path("presigned/", views.generate_s3_presigned_url_view, name="presigned post url"),
    path("success/", views.upload_successful_view, name="check success upload"),
    path("clips/", views.get_clips_view, name="get clips"),
]
