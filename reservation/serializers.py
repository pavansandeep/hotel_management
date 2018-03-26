import datetime
from rest_framework import serializers
from reservation.models import Hotel, Reservation
from reservation.utilities import normalize_date, datetime_object

class HotelSerializer(serializers.ModelSerializer):
    """
    Serializer class for Hotel Model
    """
    queryset = Hotel.objects.all()
    url = serializers.HyperlinkedIdentityField(view_name='reservation:hotel-detail', read_only=True)

    class Meta:
        model = Hotel
        fields = (
            'url', 'id', 'name', 'room_capacity', 'over_booking_capacity'
        )


class ReservationSerializer(serializers.ModelSerializer):
    """
    Serializer class for Reservation Model
    """
    url = serializers.HyperlinkedIdentityField(view_name='reservation:reservation-detail', read_only=True)

    # Including the nested serializer for hotel, we always want to show hotel information along with the reservation
    hotel_data = HotelSerializer(source='hotel', read_only=True)

    select_related_fields = ['hotel', 'hotel__name', 'hotel__room_capacity', 'hotel__over_booking_capacity']

    class Meta:
        model = Reservation
        fields = (
            'url', 'id', 'guest_name', 'guest_email', 'arrival_date', 'departure_date',
            'hotel', 'hotel_data'
        )


    def validate_arrival_date(self, value):
        """
        Arrival time no matter what is given by the user, setting this to 11AM the same day.
        Reservations typically start at a particular time on a day.
        :param value: arrival date
        :return: date time that starts with 11AM for a given date
        """
        arrival_date = normalize_date(value)
        return arrival_date

    def validate_departure_date(self, value):
        """
        Departure time no matter what is given by the user, setting this to 10AM the same day.
        Reservations typically end at a particular time on a day.
        :param value: departure date
        :return: date time that ends at 10AM for a given date
        """
        departure_date = normalize_date(value, type='departure')
        return departure_date


    # def validate_hotel(self, value):
    #     """
    #     Should validate the instance to have the same hotel object. A reservation should be for a hotel
    #     :param value:
    #     :return:
    #     """
    #     if self.instance and self.instance.hotel != value:
    #         raise serializers.ValidationError('Hotel can not be changed for a reservation')
    #
    #     return value


    def validate(self, data):
        """
        Validate on the Reservation Serializer data
        :param instance: instance of Reservation serializer data
        :return: Exception if validation fails else return validated data
        """
        error_list = []
        start_date = data.get('arrival_date', datetime_object(self.instance.arrival_date) if self.instance else None)
        end_date = data.get('departure_date', datetime_object(self.instance.departure_date) if self.instance else None)

        if end_date <= start_date:
            raise serializers.ValidationError('Departure date cannot be prior or same as the arrival date.')

        if self.instance:
            reservation_availability = self.instance.hotel.get_available_reservation_slots(start_date, end_date)
        else:
            hotel = self.initial_data.get('hotel')
            hotel = Hotel.objects.get(id=hotel)
            reservation_availability = hotel.get_available_reservation_slots(start_date, end_date)

        if reservation_availability <= 0:
            raise serializers.ValidationError('Sorry, no reservations available between the following dates {0} and {1}'.format(start_date, end_date))

        return data