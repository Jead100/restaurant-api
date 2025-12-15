from django.urls import path
from ..views.demo import (
    DemoLoginView,
    DemoMeView,
    DemoTokenRefreshView,
    DemoLogoutView,
)

app_name = "demo"

urlpatterns = [
    path("login/<str:role>/", DemoLoginView.as_view(), name="login"),
    path("me/", DemoMeView.as_view(), name="me"),
    path("token/refresh/", DemoTokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", DemoLogoutView.as_view(), name="logout"),
]
