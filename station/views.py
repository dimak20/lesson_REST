from django.db.models import Count, F
from django.http import JsonResponse
from django.shortcuts import render
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status, generics, mixins, viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, action, permission_classes
from rest_framework.generics import get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.throttling import UserRateThrottle
from rest_framework.viewsets import GenericViewSet

from station.models import (
    Bus,
    Trip,
    Facility,
    Order,
    Ticket
)
from station.permissions import IsAminAllORIsAuthenticatedOrReadOnly
from station.serializers import (
    BusSerializer,
    TripSerializer,
    TripListSerializer,
    BusListSerializer,
    FacilitySerializer,
    BusRetrieveSerializer,
    TripRetrieveSerializer,
    OrderSerializer,
    TicketSerializer,
    OrderListSerializer, BusImageSerializer,
)


class FacilityViewSet(viewsets.ModelViewSet):
    queryset = Facility.objects.all()
    serializer_class = FacilitySerializer
    # authentication_classes = (TokenAuthentication, )
    permission_classes = (IsAminAllORIsAuthenticatedOrReadOnly, )
    # permission_classes = (IsAdminUser, )
    #
    # def get_permissions(self):
    #     if self.action in ["list", "retrieve"]:
    #         return (IsAuthenticated(), )
    #     return super().get_permissions()



class BusViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    GenericViewSet
):
    queryset = Bus.objects.all()
    # throttle_classes = [UserRateThrottle]
    @staticmethod
    def _params_to_ints(query_string):
        """Converts a string '1, 2, 3' to a list of integers [1, 2, 3]"""
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return BusListSerializer
        elif self.action == "retrieve":
            return BusRetrieveSerializer
        elif self.action == "upload_image":
            return BusImageSerializer
        return BusSerializer

    def get_queryset(self):
        queryset = self.queryset
        facilities = self.request.query_params.get("facilities")
        if facilities:
            facilities = self._params_to_ints(facilities)
            queryset = queryset.filter(facilities__id__in=facilities)
        if self.action in ["list", "retrieve"]:
            return queryset.prefetch_related("facilities")
        return queryset.distinct()

    @action(
        methods=["POST",],
        detail=True,
        permission_classes=[IsAdminUser],
        url_path="upload-image"
    )
    def upload_image(self, request, pk=None):
        bus = self.get_object()
        serializer = self.get_serializer(bus, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "facilities",
                type={"type": "array", "items": {"type": "number"}},
                description="Filter by facility id (ex. ?facilities=2,3)"
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        """Get list of buses."""
        return super().list(request, *args, **kwargs)


class TripViewSet(viewsets.ModelViewSet):
    queryset = Trip.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return TripListSerializer
        if self.action == "retrieve":
            return TripRetrieveSerializer
        return TripSerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action == "list":
            queryset = (queryset
                        .select_related()
                        .annotate(tickets_available=F("bus__num_seats") - Count("tickets"))
                        )
            # queryset =  (queryset
            #              .select_related()
            #              .annotate(tickets_taken=Count("tickets"))
            #              )
        if self.action == "retrieve": #self.action in ("list", "retrieve")
            return queryset.select_related()
        return queryset.order_by("id")



class OrderSetPagination(PageNumberPagination):
    page_size = 3
    page_size_query_param = 'page_size'
    max_page_size = 20


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderSetPagination

    def get_queryset(self):
        queryset = self.queryset.filter(user=self.request.user)
        if self.action == "list":
            queryset = queryset.prefetch_related("tickets__trip__bus")
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        return OrderSerializer

class TicketViewSet(viewsets.ModelViewSet):
    queryset = Ticket.objects.all()
    serializer_class = TicketSerializer













# class BusViewSet(
#     viewsets.GenericViewSet,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin,
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.DestroyModelMixin
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer







# class BusList(
#     viewsets.GenericViewSet,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer
#
#
#
# class BusDetail(
#     viewsets.GenericViewSet,
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.DestroyModelMixin
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer








# class BusList(
#     generics.ListCreateAPIView
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer
#
#
#
# class BusDetail(
#     generics.RetrieveUpdateDestroyAPIView
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer









# class BusList(
#     generics.GenericAPIView,
#     mixins.ListModelMixin,
#     mixins.CreateModelMixin
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer
#     def get(self, request, *args, **kwargs) -> Response:
#         return self.list(request, *args, **kwargs)
#
#     def post(self, request, *args, **kwargs) -> Response:
#         return self.create(request, *args, **kwargs)
#
#
# class BusDetail(
#     generics.GenericAPIView,
#     mixins.RetrieveModelMixin,
#     mixins.UpdateModelMixin,
#     mixins.DestroyModelMixin
# ):
#     queryset = Bus.objects.all()
#     serializer_class = BusSerializer
#     def get(self, request, *args, **kwargs) -> Response:
#         return self.retrieve(request, *args, **kwargs)
#
#     def put(self, request, *args, **kwargs) -> Response:
#         return self.update(request, *args, **kwargs) #partial=True for patch
#
#     def delete(self, request, *args, **kwargs) -> Response:
#         return self.destroy(request, *args, **kwargs)







# class BusList(APIView):
#     def get(self, request):
#         bus = Bus.objects.all()
#         serializer = BusSerializer(bus, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def post(self, request):
#         serializer = BusSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# class BusDetail(APIView):
#     def get_object(self, pk):
#         return get_object_or_404(Bus, pk=pk)
#
#     def get(self, request, pk):
#         bus = self.get_object(pk)
#         serializer = BusSerializer(bus)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     def put(self, request, pk):
#         bus = self.get_object(pk)
#         serializer = BusSerializer(bus, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     def delete(self, request, pk):
#         bus = self.get_object(pk)
#         bus.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)




















# @api_view(["GET", "POST"])
# def bus_list(request):
#     if request.method == "GET":
#         bus = Bus.objects.all()
#         serializer = BusSerializer(bus, many=True)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     if request.method == "POST":
#         serializer = BusSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(["GET", "PUT", "DELETE"])
# def bus_detail(request, pk):
#     bus = get_object_or_404(Bus, pk=pk)
#
#     if request.method == "GET":
#         serializer = BusSerializer(bus)
#         return Response(serializer.data, status=status.HTTP_200_OK)
#
#     if request.method == "PUT":
#         serializer = BusSerializer(bus, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#
#     if request.method == "DELETE":
#         bus.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)