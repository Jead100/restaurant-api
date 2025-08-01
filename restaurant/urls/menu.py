from rest_framework.routers import DefaultRouter

from restaurant.views.menu import MenuItemViewSet, CategoryViewSet

router = DefaultRouter()
router.register("items", MenuItemViewSet, basename="menuitem")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = router.urls
