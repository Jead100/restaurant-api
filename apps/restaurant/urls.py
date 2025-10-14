from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import MenuItemViewSet, CategoryViewSet, CartViewSet, OrderViewSet


app_name = "restaurant"

router = DefaultRouter()
router.register("items", MenuItemViewSet, basename="menuitem")
router.register("categories", CategoryViewSet, basename="category")
router.register("cart", CartViewSet, basename="cart")
router.register("orders", OrderViewSet, basename="order")

urlpatterns = [path("", include(router.urls))]
