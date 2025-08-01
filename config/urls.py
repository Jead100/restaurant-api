from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth (via Djoser)
    path("auth/", include("djoser.urls")),
    path("auth/token/", include("djoser.urls.authtoken")),

    # App endpoints
    path("api/menu/", include("restaurant.urls.menu")),
    path("api/cart/", include("restaurant.urls.cart")),
    path("api/orders/", include("restaurant.urls.order")),
    path("api/users/", include("users.urls")),
]
