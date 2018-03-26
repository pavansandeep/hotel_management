import datetime
import json
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from copy import deepcopy, copy
from unittest import TestCase
from django.test import TestCase
from reservation.models import Hotel, Reservation
from reservation.utilities import normalize_date
from rest_framework.test import APITestCase

# Create your tests here.
class TestHotel(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='test hotel', room_capacity=4, over_booking_capacity=50)
        self.hotel2 = Hotel.objects.create(name='test hotel2', room_capacity=2, over_booking_capacity=50)

        # start and end dates
        self.start_date = normalize_date(datetime.datetime.now())
        self.end_date = normalize_date(datetime.datetime.now()+datetime.timedelta(3), type="departure")

        # start and end dates
        self.start_date2 = self.start_date-datetime.timedelta(1)
        self.end_date2 = self.start_date+datetime.timedelta(2)

        self.reservation1 = Reservation.objects.create(guest_name="test name", guest_email="test_name@smth.com",
            arrival_date=self.start_date, departure_date= self.end_date, hotel=self.hotel2)

        self.reservation2 = Reservation.objects.create(guest_name="test name", guest_email="test_name@smth.com",
            arrival_date=self.start_date2, departure_date= self.end_date2, hotel=self.hotel2)

    def test_get_over_booking_capacity(self):
        # Testing booking capacity for the hotel object
        self.assertTrue(self.hotel.get_over_booking_capacity()==2)

        # Decreased the over booking capacity to 25 for the hotel object
        self.hotel.over_booking_capacity = 10
        self.hotel.save()

        # Should not return a float value, return value is 0 != 0.4
        self.assertFalse(self.hotel.get_over_booking_capacity()==0.4)

        self.hotel.over_booking_capacity = 25
        self.hotel.save()

        # Returns an integer 1
        self.assertTrue(self.hotel.get_over_booking_capacity()==1)

    def test_get_available_reservation_slots(self):

        # There are two reservations already and since over booking is 1, there is one available slot
        self.assertTrue(self.hotel2.get_available_reservation_slots(self.start_date, self.end_date)==1)

        self.reservation3 = Reservation.objects.create(guest_name="test name", guest_email="test.name@smth.com",
            arrival_date=self.start_date2, departure_date=self.end_date2, hotel=self.hotel2)

        # There are three reservations now, available reservation slots should be 0
        self.assertTrue(self.hotel2.get_available_reservation_slots(self.start_date, self.end_date)==0)

        self.reservation4 = Reservation.objects.create(guest_name="test name", guest_email="test.name@smth.com",
            arrival_date=self.start_date, departure_date=self.end_date, hotel=self.hotel2)


class TestHotelList(APITestCase):

    def test_get(self):
        url = reverse('reservation:hotel-list')
        response = self.client.get(url, format='json', accept='application/json')
        # Since there are no hotel objects created, len(results) should be zero
        self.assertTrue(len(response.data['results'])==0)

        # Testing post method before making a GET request on /api/hotels
        self.test_post()
        response = self.client.get(url, format='json', accept='application/json')
        # since there are two hotel objects created in the test_post method, len(results) is two
        self.assertEqual(len(response.data['results']), 2)

    def test_post(self):
        url = reverse('reservation:hotel-list')
        data = {"name": "hotel foo", "room_capacity": 0}
        response = self.client.post(url, data, format='json')

        # Bad request, because room_capacity can not be zero
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Checking if room_capacity is available in response because an error is expected that it should be atleast 1
        self.assertIn('room_capacity', response.data)

        # No Hotel objects were created so far
        self.assertEqual(Hotel.objects.count(), 0)

        # Changing the room capacity to 1
        data['room_capacity'] = 1
        response = self.client.post(url, data, format='json')

        # Response should return a 201 status that resource is created,
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.hotel_id = response.data['id']

        # The default value for over_booking_capacity is set, notice that it is not passed as part of in the above
        # request
        self.assertEqual(response.data['over_booking_capacity'], 0)
        self.assertEqual(Hotel.objects.count(), 1)

        # making another POST request to the url.
        data = {"name": "hotel bar", "room_capacity": 10, "over_booking_capacity": 25}
        response = self.client.post(url, data, format='json')

        # Response should return a 201 status that resource is created,
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.hotel_id2 = response.data['id']
        self.assertEqual(Hotel.objects.count(), 2)


class TestHotelDetail(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='test hotel', room_capacity=4, over_booking_capacity=50)
        self.hotel2 = Hotel.objects.create(name='test hotel2', room_capacity=2, over_booking_capacity=50)
        self.url = '/api/hotels/'

    def test_get(self):
        response = self.client.get(self.url+str(self.hotel.id), format='json', accept='application/json')

        # Checking if 200 status code returned by the response
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        # Checking if response contains id same as self.hotel's id
        self.assertTrue(response.data['id'], self.hotel.id)

        response = self.client.get(self.url+str(10000), format='json', accept='application/json')
        # Checking if 404 error is returned, since there is no hotel with id 10000
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_put(self):
        data = {"name": "test hotel", "room_capacity": 4}
        response = self.client.put(self.url+str(self.hotel.id), json.dumps(data), format='json', content_type='application/json')

        # Bad request, since put requires the whole body and over_booking_capacity is missed
        self.assertTrue(response.status_code, status.HTTP_200_OK)

        # setting over booking capacity as 25
        data["over_booking_capacity"] = 25
        response = self.client.put(self.url+str(self.hotel.id), json.dumps(data),
                                   format='json', content_type='application/json')

        # Should succesfully update the hotel with the new over booking capacity
        self.assertTrue(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['over_booking_capacity'], 25)

        # setting room capacity to 0
        data["room_capacity"] = 0
        response = self.client.put(self.url+str(self.hotel.id), json.dumps(data),
                                   format='json', content_type='application/json')

        # Bad request, because room_capacity can not be zero
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Checking if room_capacity is available in response because an error is expected that it should be atleast 1
        self.assertIn('room_capacity', response.data)

    def test_patch(self):
        data = {"name": "test hotel foo"}
        # Making a patch call to change the name of hotel2
        response = self.client.patch(self.url+str(self.hotel2.id), json.dumps(data), format='json',
                                     content_type='application/json')

        # Status code should be 200 because it should be successfully update
        self.assertTrue(response.status_code, status.HTTP_200_OK)

        # checking if the response data has the new name passed above
        self.assertEqual(response.data['name'], "test hotel foo")

        data= {"room_capacity": 0}
        response = self.client.put(self.url+str(self.hotel.id), json.dumps(data),
                                   format='json', content_type='application/json')

        # Bad request, because room_capacity can not be zero
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Checking if room_capacity is available in response because an error is expected that it should be atleast 1
        self.assertIn('room_capacity', response.data)


    def test_delete(self):
        hotel2_id = self.hotel2.id
        response = self.client.delete(self.url+str(hotel2_id), accept='application/json')
        # Response status code is 204, since it is deleted successfully
        self.assertTrue(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.url+str(hotel2_id), accept='application/json')
        # Response status code is 404, since hotel 2 was delete in the previous request
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)


class TestReservationList(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='test hotel', room_capacity=1, over_booking_capacity=50)

    def test_get(self):
        url = reverse('reservation:reservation-list')
        response = self.client.get(url, format='json', accept='application/json')
        # Since there are no reservation objects created, len(results) should be zero
        self.assertTrue(len(response.data['results'])==0)

        # Testing post method before making a GET request on /api/reservations
        self.test_post()
        response = self.client.get(url, format='json', accept='application/json')
        # since there is a reservation object created in the test_post method, len(results) is one
        self.assertEqual(len(response.data['results']), 1)

    def test_post(self):
        url = reverse('reservation:reservation-list')
        data = {}
        response = self.client.post(url, data, format='json')

        # Bad request, because room_capacity can not be zero
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # All the fields are required in the reservation model
        self.assertEqual(len(response.data), 5)

        # No Hotel objects were created so far
        self.assertEqual(Reservation.objects.count(), 0)

        data = {"guest_name": "tester", "guest_email": "tester@foo.com", "arrival_date": "2018-03-26T00:00:00",
                "departure_date": "2018-03-26T00:00:00", "hotel": self.hotel.id}
        response = self.client.post(url, data, format='json')

        # Bad request, because departure date cannot be same as arrival_date
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # There is details with one non_field_errors
        self.assertEqual(len(response.data), 1)

        # The response data has non_field_errors key
        self.assertIn('non_field_errors', response.data)

        # updating departure_date, hotel in the data dictionary
        data["departure_date"] = "2018-03-27T00:00:00"
        data["hotel"]=1000

        response = self.client.post(url, data, format='json')

        # Bad request, because departure date cannot be same as arrival_date
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # There is details with one error since we passed invalid id for the hotel key
        self.assertEqual(len(response.data), 1)

        # Response should have error regarding hotel
        self.assertIn('hotel', response.data)

        data["hotel"] = self.hotel.id

        response = self.client.post(url, data, format='json')

        # Response status code should be 201
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.reservation_id = response.data['id']

        # Number of Reservation objects is now one, since the resource was successfully created
        self.assertEqual(Reservation.objects.count(), 1)

        response = self.client.post(url, data, format='json')

        # Check number of reservations possible for the start_date 2018-03-26T00:00:00 and end_date 2018-03-27T00:00:00
        start_date = normalize_date(datetime.datetime(2018, 03, 26, 11, 0, 0))
        end_date = normalize_date(datetime.datetime(2018, 03, 27, 11, 0, 0), type='departure')
        reservation_slots_available = self.hotel.get_available_reservation_slots(start_date, end_date)

        # Response status code is 400, since only one reservation is possible
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Non Field error should say "Sorry, no reservations available between the following dates 2018-03-26 11:00:00 and 2018-03-27 10:00:00
        self.assertIn("non_field_errors", response.data)

        self.assertEqual(response.data['non_field_errors'], ["Sorry, no reservations available between the"
                                                            " following dates {0} and {1}".format(start_date, end_date)])


class TestReservationDetail(TestCase):
    def setUp(self):
        self.hotel = Hotel.objects.create(name='test hotel', room_capacity=1, over_booking_capacity=100)

        # start and end dates
        # Eg: start date: 2018-03-26T11:00:00, end_date is 3 days from start_date which is 2018-03-29T10:00:00
        self.start_date = normalize_date(datetime.datetime.now())
        self.end_date = normalize_date(datetime.datetime.now()+datetime.timedelta(3), type="departure")

        # start and end dates
        # Based on the above start_date, start_date2: 2018-03-25T11:00:00, end_date2: 2018-03-28T10:00:00 (Just for Examples)
        self.start_date2 = normalize_date(self.start_date-datetime.timedelta(1))
        self.end_date2 = normalize_date(self.start_date+datetime.timedelta(2), type="departure")

        self.reservation1 = Reservation.objects.create(guest_name="test name", guest_email="test_name@smth.com",
            arrival_date=self.start_date, departure_date= self.end_date, hotel=self.hotel)

        self.reservation2 = Reservation.objects.create(guest_name="test name", guest_email="test_name@smth.com",
            arrival_date=self.start_date2, departure_date= self.end_date2, hotel=self.hotel)

        # start and end dates
        # Based on above start date, start_date3: 2018-03-29T11:00:00, end_date2: 2018-03-31T10:00:00 (Just for Examples)
        self.start_date3 = normalize_date(self.start_date+datetime.timedelta(3))
        self.end_date3 = normalize_date(self.start_date+datetime.timedelta(5), type="departure")
        self.reservation3 = Reservation.objects.create(guest_name="test name", guest_email="test_name@smth.com",
            arrival_date=self.start_date3, departure_date= self.end_date3, hotel=self.hotel)
        self.url = '/api/reservations/'

    def test_get(self):
        pass

    def test_put(self):
        # Based on the start_date3, this will be start_date: 2018-03-27T11:00:00
        start_date = (self.start_date3-datetime.timedelta(2)).strftime('%Y-%m-%dT%H:%M:%S')
        end_date = (self.end_date3).strftime('%Y-%m-%dT%H:%M:%S')

        data = {}
        response = self.client.put(self.url+str(self.reservation3.id), json.dumps(data), format='json', content_type='application/json')

        # Bad request since body is empty and PUT requires the whole body to update the reservation
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)
        # since reservation object required all available 5 fields to be passed and since none of them is passed,
        #  they will be shown as errors in response body
        self.assertEqual(len(response.data), 5)

        data = {"guest_name":"test name", "guest_email":"test_name@smth.com",
            "arrival_date": start_date, "departure_date": end_date, "hotel": self.hotel.id}
        response = self.client.put(self.url+str(self.reservation3.id), json.dumps(data), format='json', content_type='application/json')

        # Bad request, since there will be a reservation overlap
        self.assertTrue(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Since the reservation overlaps with the other two reservations ie., self.reservation1, self.reservation2
        #  and maximum booking capacity is 2
        self.assertIn('non_field_errors', response.data)

        start_date = (self.start_date3-datetime.timedelta(1)).strftime('%Y-%m-%dT%H:%M:%S')
        data = {"guest_name":"test name", "guest_email":"test_name@smth.com",
            "arrival_date": start_date, "departure_date": end_date, "hotel": self.hotel.id}
        response = self.client.put(self.url+str(self.reservation3.id), json.dumps(data), format='json', content_type='application/json')

        # PUT request should be successful, since there will be no collision of dates availability for reservation
        self.assertTrue(response.status_code, status.HTTP_200_OK)


    def test_patch(self):
        start_date = (self.start_date3-datetime.timedelta(2)).strftime('%Y-%m-%dT%H:%M:%S')
        data = {"arrival_date": start_date}
        response = self.client.patch(self.url+str(self.reservation3.id), json.dumps(data), format='json', content_type='application/json')

        # Bad request, since there will be a reservation overlap
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn('non_field_errors', response.data)

    def test_delete(self):
        reservation3_id = self.reservation3.id
        response = self.client.delete(self.url+str(reservation3_id), accept='application/json')
        # Response status code is 204, since reservation is deleted successfully
        self.assertTrue(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.url+str(reservation3_id), accept='application/json')
        # Response status code is 404, since reservation3 was deleted in the previous request
        self.assertTrue(response.status_code, status.HTTP_404_NOT_FOUND)


class TestNormalize_date(TestCase):
    def setUp(self):
        self.date = ''
        self.date2 = None
        self.date3 = '2016-03-26T00:00:00'
        self.date4 = datetime.datetime(2016, 03, 26, 0, 0, 0)
        self.type = 'arrival'
        self.type2 = 'departure'

    def test_normalize_date(self):
        # Since self.date is not an instance of datetime.datetime, None is returned
        self.assertIsNone(normalize_date(self.date))

        # Since self.date2 is None, None is returned
        self.assertIsNone(normalize_date(self.date2))

        # since self.date3 is not an instance of str, None is returned
        self.assertIsNone(normalize_date(self.date3))

        res_date = normalize_date(self.date4)
        # Since self.date4 is a datetime.datetime instance, the return type is also a datetime.datetime instance
        self.assertTrue(isinstance(res_date, datetime.datetime))

        # The default type is 'arrival' and hence the hour should be 11, minute should be 0, seconds should be 0
        self.assertEqual(res_date.hour, 11)
        self.assertEqual(res_date.minute, 0)
        self.assertEqual(res_date.second, 0)

        res_date = normalize_date(self.date4, type=self.type2)
        # Since self.date4 is a datetime.datetime instance, the return type is also a datetime.datetime instance
        self.assertTrue(isinstance(res_date, datetime.datetime))

        # since type is 'departure' the hour should be 10, minute should be 0, seconds should be 0
        self.assertEqual(res_date.hour, 10)
        self.assertEqual(res_date.minute, 0)
        self.assertEqual(res_date.second, 0)