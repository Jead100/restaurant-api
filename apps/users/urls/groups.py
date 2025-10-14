from django.urls import path, include
from rest_framework.routers import DefaultRouter

from ..views.groups import ManagerGroupViewSet, DeliveryCrewGroupViewSet

app_name = "users"

router = DefaultRouter()
router.register("manager", ManagerGroupViewSet, basename="manager-group")
router.register(
    "delivery-crew",
    DeliveryCrewGroupViewSet,
    basename="delivery-crew-group",
)
urlpatterns = [path("groups/", include(router.urls))]
