from django.urls import path

from socials import views

urlpatterns = [
    path("get/", views.get_socials_view, name="get socials"),
    path("update/", views.save_socials_view, name="update socials"),
]
