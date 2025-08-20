from rest_framework.routers import DefaultRouter
from users.views.groups import ManagerGroupViewSet, DeliveryCrewGroupViewSet

router = DefaultRouter()
router.register("groups/manager/users", ManagerGroupViewSet, basename="manager-group")
router.register(
    "groups/delivery-crew/users",
    DeliveryCrewGroupViewSet,
    basename="delivery-crew-group",
)

urlpatterns = router.urls
