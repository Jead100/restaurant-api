from django.urls import path
from ..views.demo import (
    DemoLoginView,
    DemoMeView,
    DemoTokenRefreshView,
    DemoLogoutView,
)


urlpatterns = [
    path(
        "demo-login/<str:role>/",
        DemoLoginView.as_view(),
        name="demo-login",
    ),
    path(
        "demo-me/",
        DemoMeView.as_view(),
        name="auth-me",
    ),
    path(
        "demo-token/refresh/",
        DemoTokenRefreshView.as_view(),
        name="demo_token_refresh",
    ),
    path(
        "demo-logout/",
        DemoLogoutView.as_view(),
        name="auth-logout",
    ),  # blacklist current refresh
]
