from django.urls import path

from ..views.me import CurrentUserView

app_name = "me"

urlpatterns = [
    path("users/me/", CurrentUserView.as_view(), name="current-user"),
]
