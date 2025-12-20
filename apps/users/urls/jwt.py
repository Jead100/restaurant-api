from django.urls import path

from ..views.jwt import JWTCreateView, JWTRefreshView, JWTVerifyView

app_name = "jwt"

urlpatterns = [
    path("jwt/create/", JWTCreateView.as_view(), name="jwt-create"),
    path("jwt/refresh/", JWTRefreshView.as_view(), name="jwt-refresh"),
    path("jwt/verify/", JWTVerifyView.as_view(), name="jwt-verify"),
]
