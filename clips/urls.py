from django.urls import path

from clips import views

urlpatterns = [
    path("check/", views.upload_check_view, name="upload check"),
    path("upload/", views.upload_clip_view, name="upload clip"),
]
