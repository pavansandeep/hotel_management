from django.conf.urls import include, url
from reservation import views

urlpatterns = [

    # This is the api root for reservations
    url(r'^$', views.api_root, name='api'),

    # Api for to list and create hotels
    url(r'^/hotels$', views.HotelList.as_view(), name='hotel-list'),

    # Api for view, update and delete for a specific hotel
    url(r'^/hotels/(?P<pk>[0-9]+)$', views.HotelDetail.as_view(), name='hotel-detail'),

    # Api for to create and view the reservations
    url(r'^/reservations$', views.ReservationList.as_view(), name='reservation-list'),

    # Api to view, update and delete a specific reservation
    url(r'^/reservations/(?P<pk>[0-9]+)$', views.ReservationDetail.as_view(), name='reservation-detail')
]