from debug_toolbar.toolbar import debug_toolbar_urls
from django.urls import path, include
from station.views import BusViewSet, TripViewSet, FacilityViewSet, OrderViewSet, TicketViewSet
from rest_framework import routers


app_name = "station"


router = routers.DefaultRouter()
router.register("buses", BusViewSet)
router.register("trips", TripViewSet)
router.register("facilities", FacilityViewSet)
router.register("orders", OrderViewSet)
router.register("tickets", TicketViewSet)
# urlpatterns = router.urls

# bus_list = BusViewSet.as_view(
#     actions={
#         "get": "list",
#         "post": "create"
#     }
# )
# bus_detail = BusViewSet.as_view(
#     actions={
#         "get": "retrieve",
#         "put": "update",
#         "patch": "partial_update",
#         "delete": "destroy"
#     }
# )
#
urlpatterns = [
    path("", include(router.urls)),
]


# urlpatterns = [
#     path("buses/", bus_list, name="bus_list"),
#     path("buses/<int:pk>/", bus_detail, name="bus_detail"),
# ]