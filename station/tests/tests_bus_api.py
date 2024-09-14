from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APIClient

from station.models import Bus, Facility
from station.serializers import BusSerializer, BusListSerializer, BusRetrieveSerializer

BUS_URL = reverse("station:bus-list")
def detail_url(bus_id): #127.0.0.1:8000/api/v1/station/buses/<bus_id>/
    return reverse("station:bus-detail", args=(str(bus_id),)) #args=[str(bus.id)]


def sample_bus(**params) -> Bus:
    defaults = {
        "info": "AA 0000 BB",
        "num_seats": 50,
    }
    defaults.update(params)
    return Bus.objects.create(**defaults)


class UnauthenticatedBusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BUS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBusApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="test@test.test", password="testpassword"
        )
        self.client.force_authenticate(self.user)

    def test_bus_list(self):
        sample_bus()
        bus_with_facilities = sample_bus()

        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="WC")

        bus_with_facilities.facilities.add(facility_1, facility_2)

        res = self.client.get(BUS_URL)
        buses = Bus.objects.all()
        serializer = BusListSerializer(buses, many=True)
        # self.assertEqual(res.data["results"], serializer.data) for paginated result
        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_buses_by_facilities(self):
        bus_without_facility = sample_bus()
        bus_with_facility_1 = sample_bus(info="AA 0001 BB")
        bus_with_facility_2 = sample_bus(info="AA 0002 BB")

        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="WC")

        bus_with_facility_1.facilities.add(facility_1)
        bus_with_facility_2.facilities.add(facility_2)

        res = self.client.get(
            BUS_URL,
            {"facilities": f"{facility_1.id},{facility_2.id}"}   #?facilities=1,2
        )

        serializer_without_facilities = BusListSerializer(bus_without_facility)
        serializer_bus_facility_1 = BusListSerializer(bus_with_facility_1)
        serializer_bus_facility_2 = BusListSerializer(bus_with_facility_2)

        self.assertIn(serializer_bus_facility_1.data, res.data)  #["results"]
        self.assertIn(serializer_bus_facility_2.data, res.data)
        self.assertNotIn(serializer_without_facilities.data, res.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


    def test_retrieve_bus_detail(self):
        bus = sample_bus()
        bus.facilities.add(Facility.objects.create(name="WiFi"))

        url = detail_url(bus.id)
        res = self.client.get(url)

        serializer = BusRetrieveSerializer(bus)

        self.assertEqual(res.data, serializer.data)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_create_bus_forbidden(self):
        payload = {
            "info": "AA 9999 BB",
            "num_seats": 20
        }

        res = self.client.post(BUS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class AdminBusTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email="admin@admin.test",
            password="testpassword",
            is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_create_bus(self):
        # Facility.objects.create(name="WiFi")
        payload = {
            "info": "AA 9999 BB",
            "num_seats": 20
        }

        res = self.client.post(BUS_URL, payload)
        bus = Bus.objects.get(id=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        for key in payload:
            self.assertEqual(payload[key], getattr(bus, key))


    def test_create_bus_with_facilities(self):
        facility_1 = Facility.objects.create(name="WiFi")
        facility_2 = Facility.objects.create(name="WC")
        payload = {
            "info": "AA 9999 BB",
            "num_seats": 20,
            "facilities": [facility_1.id, facility_2.id]
        }

        res = self.client.post(BUS_URL, payload)
        bus = Bus.objects.get(id=res.data["id"])
        facilities = bus.facilities.all()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertIn(facility_1, facilities)
        self.assertIn(facility_2, facilities)
        self.assertEqual(facilities.count(), 2)

    def test_delete_bus_not_allowed(self):
        bus = sample_bus()

        url = detail_url(bus.id)

        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
