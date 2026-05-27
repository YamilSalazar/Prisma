from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    path("", views.home, name="home"),
    path("mapa/", views.map_view, name="map"),
    path("parques/", views.park_list, name="park_list"),
    path("parques/<slug:slug>/", views.park_detail, name="park_detail"),
    path("login/", views.login_view, name="login"),
    path("registro/", views.register, name="register"),
    path("recuperar/", views.password_reset, name="password_reset"),
    path("reservacion/datos/", views.booking_details, name="booking_details"),
    path("reservacion/resumen/", views.booking_summary, name="booking_summary"),
    path("reservacion/pago/", views.booking_payment, name="booking_payment"),
    path("reservacion/confirmacion/", views.booking_confirmation, name="booking_confirmation"),
    path("mis-reservaciones/", views.reservations, name="reservations"),
    path("mi-cuenta/", views.account, name="account"),
    path("cambiar-password/", views.change_password, name="change_password"),
]
