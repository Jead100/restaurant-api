from rest_framework.routers import DefaultRouter

from restaurant.views.order import OrderViewSet

router = DefaultRouter()
router.register("", OrderViewSet, basename="order")

urlpatterns = router.urls
