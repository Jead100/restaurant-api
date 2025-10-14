from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    # Home page
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # App endpoints
    path(
        "api/v1/restaurant/",
        include(("apps.restaurant.urls", "restaurant"), namespace="restaurant"),
    ),
    path(
        "api/v1/users/", include(("apps.users.urls.groups", "users"), namespace="users")
    ),
    # OpenAPI schema & UIs
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

if settings.DEBUG:
    urlpatterns += [path("admin/", admin.site.urls)]

EXPOSE_DJOSER = settings.DEBUG or not settings.DEMO_MODE
if EXPOSE_DJOSER:
    # Always expose Djoser endpoints for full user management
    # when DEBUG=True or DEMO_MODE=False
    urlpatterns += [
        path("api/v1/auth/", include("djoser.urls")),
        path("api/v1/auth/", include("djoser.urls.jwt")),
    ]

if settings.DEMO_MODE:
    # Only add/expose demo user endpoints when DEMO_MODE=True
    urlpatterns += [
        path(
            "api/v1/auth/",
            include(("apps.users.urls.demo", "users"), namespace="demo-users"),
        )
    ]
