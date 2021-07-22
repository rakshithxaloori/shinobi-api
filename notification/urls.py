from django.urls import path

from notification import views

urlpatterns = [
    path(
        "<int:begin_index>/<int:end_index>/",
        views.notifications_view,
        name="notifications",
    )
]
