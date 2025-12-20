from django.conf import settings
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

DEBUG = settings.DEBUG
DEMO_MODE = settings.DEMO_MODE
EXPOSE_DJOSER = settings.EXPOSE_DJOSER


urlpatterns = [
    # Home page
    path("", TemplateView.as_view(template_name="home.html"), name="home"),
    # App endpoints
    path(
        "api/v1/restaurant/",
        include("apps.restaurant.urls", namespace="restaurant"),
    ),
    path("api/v1/users/", include("apps.users.urls.groups", namespace="users")),
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

if DEBUG:
    urlpatterns += [path("admin/", admin.site.urls)]

if DEBUG or not DEMO_MODE:
    # Always expose JWT when DEBUG=True or DEMO_MODE=False
    urlpatterns += [
        path("api/v1/auth/", include("apps.users.urls.jwt", namespace="jwt")),
    ]

    # In DEBUG, optionally expose Djoser
    if DEBUG and EXPOSE_DJOSER:
        urlpatterns += [
            path("api/v1/auth/", include("djoser.urls")),
        ]
    else:
        # A simple minimal profile endpoint will suffice
        urlpatterns += [
            path("api/v1/auth/", include("apps.users.urls.me", namespace="me")),
        ]

if DEMO_MODE:
    # Only add/expose demo user management endpoints when DEMO_MODE=True
    urlpatterns += [
        path("api/v1/auth/demo/", include("apps.users.urls.demo", namespace="demo"))
    ]
