from rest_framework.routers import DefaultRouter

from restaurant.views.cart import CartViewSet

router = DefaultRouter()
router.register("items", CartViewSet, basename="cart")

urlpatterns = router.urls
