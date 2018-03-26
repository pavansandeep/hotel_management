# coding=utf-8
import datetime
from django.db import models
from django.db.models import Q
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from reservation.utilities import normalize_date

# Create your models here.
class TimeStampedModel(models.Model):
    """
    Base class for any model which needs to maintain created and last_modified time of the objects.

    Attributes:
        created_time: The time when the object was created and added to the database
        last_modified_time: The time when the object was last modified
    """
    class Meta:
        abstract = True

    created_time = models.DateTimeField(auto_now_add=True)
    last_modified_time = models.DateTimeField(auto_now=True)


class Hotel(models.Model):
    """
    Hotel class which maintains attributes of a hotel
    """
    # Name of the hotel
    name = models.CharField(max_length=255, null=False, blank=False)

    # Total Number of Rooms in the hotel
    room_capacity = models.PositiveIntegerField(null=False, blank=False, validators=[MinValueValidator(1)])

    # Overbooking Capacity for the hotel rooms. This is a percentage of room capacity
    over_booking_capacity = models.PositiveIntegerField(null=False, blank=False, default=0)

    def __unicode__(self):
        """
        :return: Unicode representation of the Hotel object
        """
        return unicode(self.name)

    def get_over_booking_capacity(self):
        """
            Get total number of rooms that can be overbooked.
        """
        return (self.room_capacity*self.over_booking_capacity)//100

    def get_available_reservation_slots(self, start_date, end_date):
        """
            Given a start date, get the number of reservation slots available till the end date
        """

        # total capacity is the sum of room_capacity and the number of over bookings allowed.
        total_capacity = self.room_capacity+self.get_over_booking_capacity()

        start_date = normalize_date(start_date, type='arrival')
        end_date = normalize_date(end_date, type='departure')

        if not start_date or not end_date:
            raise ValidationError('Arrival or departure dates format is not correct')


        # Reservation count between specific start and end dates. Filtering the existing reservations based on the given
        #  start and end date.
        # Below are the following possibilities. Only one of the below condition will be true for each reservation.
        # 1. Arrival date is same as start date filter that reservation (or)
        # 2. Departure date is same as end date filter that reservation (or)
        # 3. Arrival date < start date and Departure date > start date and departure date < end date (or)
        # 4. Arrival date < end date and Departure date > end date and Arrival date > start date (or)
        # 5. Arrival date > start date and Departure date < end date (or)
        # 6. Arrival date < start date and Departyre date > end date
        reservation_count = self.hotel_reservations.filter(Q(arrival_date=start_date) |
                                                           Q(departure_date=end_date) |
                                                      Q(arrival_date__lt=start_date, departure_date__gt=start_date,
                                                        departure_date__lt=end_date) |
                                                      Q(arrival_date__lt=end_date,
                                                        departure_date__gt=end_date, arrival_date__gt=start_date) |
                                                      Q(arrival_date__gt=start_date, departure_date__lt=end_date) |
                                                      Q(arrival_date__lt=start_date, departure_date__gt=end_date)
                                                      ).count()

        # gives the total vacancy available for the given range.
        return total_capacity-reservation_count


class Reservation(TimeStampedModel):
    """
    Reservation class to keep track of reservations made by a Guest
    """

    # Guest's Name for whom the reservation was made
    guest_name = models.CharField(max_length=255, null=False, blank=False)

    # Guest's email address
    guest_email = models.EmailField(null=False, blank=False)

    # Arrival date
    arrival_date = models.DateTimeField(null=False, blank=False)

    # Departure date
    departure_date = models.DateTimeField(null=False, blank=False)

    # Each reservation should be mapped to a hotel
    hotel = models.ForeignKey(Hotel, null=False, blank=False, related_name='hotel_reservations')


    def __unicode__(self):
        """
        :return: Unicode representation of the Reservation object
        """
        return unicode(self.pk)


