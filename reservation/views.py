import logging
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import filters, generics
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from django.db import transaction
from reservation.serializers import HotelSerializer, ReservationSerializer
from reservation.models import Hotel, Reservation

logger = logging.getLogger('restAPI')

# Create your views here.

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

@api_view(('GET',))
def api_root(request):
    return Response({
        'hotels': reverse('reservation:hotel-list', request=request),
        'reservations': reverse('reservation:reservation-list', request=request)
    })


class HotelList(generics.ListCreateAPIView):
    """
    List all the hotels (GET method), Create a hotel (POST method) based on Http methods.
    :param request:
    :return:
    """
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        # This gives the list of all hotels
        return super(HotelList, self).get(request, *args, **kwargs)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        # Creates a new Hotel object
        logger.info('Adding a new hotel from the ip= {0}'.format(get_client_ip(request)))
        return super(HotelList, self).post(request, *args, **kwargs)


class HotelDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get a hotel detail (GET method), Update a hotel detail (PUT method), Partial Update a hotel (PATCH method),
    Delete a hotel (DELETE method) based on Http methods.
    :param request: lookup_field is pk, which is taken from the url
    :return:
    """
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer

    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        # Retrieves a specific hotel given a pk value
        return super(HotelDetail, self).get(request, *args, **kwargs)

    @transaction.atomic()
    def put(self, request, *args, **kwargs):
        # Updates a specific hotel given a pk value
        logger.info('Updating the hotel.id= {0} from the ip= {1}'.format(kwargs['pk'], get_client_ip(request)))
        return super(HotelDetail, self).put(request, *args, **kwargs)

    @transaction.atomic()
    def patch(self, request, *args, **kwargs):
        # Partially update a specific hotel given a pk value
        logger.info('Patching the hotel.id= {0} from the ip= {1}'.format(kwargs['pk'], get_client_ip(request)))
        return super(HotelDetail, self).patch(request, *args, **kwargs)

    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        # deletes a hotel given a pk value
        logger.info('Deleting the hotel.id= {0} from the ip= {1}'.format(kwargs['pk'], get_client_ip(request)))
        return super(HotelDetail, self).delete(request, *args, **kwargs)


class ReservationList(generics.ListCreateAPIView):
    """
    List all the reservations (GET method), Create a reservation (POST method) based on Http methods.
    :param request:
    :return:
    """
    queryset = Reservation.objects.select_related(*ReservationSerializer.select_related_fields).all()
    serializer_class = ReservationSerializer

    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        # This gives the list of all hotels
        return super(ReservationList, self).get(request, *args, **kwargs)

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        # Creates a new Hotel object
        logger.info('Adding a new reservation from the ip= {0}'.format(get_client_ip(request)))
        return super(ReservationList, self).post(request, *args, **kwargs)


class ReservationDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    Get a reservation detail (GET method), Update a reservation (PUT method), Partial Update a reservation
     (PATCH method), Delete a reservation (DELETE method) based on Http methods.
    :param request: lookup_field is pk, which is taken from the url
    :return:
    """
    queryset = Reservation.objects.select_related(*ReservationSerializer.select_related_fields).all()
    serializer_class = ReservationSerializer


    @transaction.atomic()
    def get(self, request, *args, **kwargs):
        # Retrieves a specific reservation given a pk value
        return super(ReservationDetail, self).get(request, *args, **kwargs)

    @transaction.atomic()
    def put(self, request, *args, **kwargs):
        # Updates a specific reservation given a pk value
        logger.info('Updating the reservation.id={0} from the ip= {1}'.format(kwargs['pk'], get_client_ip(request)))
        return super(ReservationDetail, self).put(request, *args, **kwargs)

    @transaction.atomic()
    def patch(self, request, *args, **kwargs):
        # Partially update a specific reservation given a pk value
        logger.info('Patching the reservation.id={0} from the ip= {1}'.format(kwargs['pk'], get_client_ip(request)))
        return super(ReservationDetail, self).patch(request, *args, **kwargs)

    @transaction.atomic()
    def delete(self, request, *args, **kwargs):
        # deletes a reservation given a pk value
        logger.info('Deleting the reservation.id={0} from the ip= {1}'.format(kwargs['pk'], get_client_ip(request)))
        return super(ReservationDetail, self).delete(request, *args, **kwargs)