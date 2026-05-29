from django.urls import path

from . import views


app_name = "core"

urlpatterns = [
    # ── Público ───────────────────────────────────────────────────
    path("", views.home, name="home"),
    path("mapa/", views.map_view, name="map"),
    path("parques/", views.park_list, name="park_list"),
    path("parques/<slug:slug>/", views.park_detail, name="park_detail"),

    # ── Auth ──────────────────────────────────────────────────────
    path("login/", views.login_view, name="login"),
    path("registro/", views.register, name="register"),
    path("recuperar/", views.password_reset, name="password_reset"),

    # ── Flujo de reservación ──────────────────────────────────────
    path("reservacion/datos/", views.booking_details, name="booking_details"),
    path("reservacion/resumen/", views.booking_summary, name="booking_summary"),
    path("reservacion/pago/", views.booking_payment, name="booking_payment"),
    path("reservacion/confirmacion/", views.booking_confirmation, name="booking_confirmation"),

    # ── Cuenta de usuario ─────────────────────────────────────────
    path("mis-reservaciones/", views.reservations, name="reservations"),
    path("mi-cuenta/", views.account, name="account"),
    path("cambiar-password/", views.change_password, name="change_password"),

    # ── Panel admin (requiere is_staff=True) ──────────────────────
    path("fila-admin/", views.admin_panel, name="admin_panel"),
    path("fila-admin/parques/", views.admin_parques, name="admin_parques"),
    path("fila-admin/parques/agregar/", views.admin_agregar_parque, name="admin_agregar_parque"),
    path("fila-admin/parques/<slug:slug>/editar/", views.admin_editar_parque, name="admin_editar_parque"),
    path("fila-admin/parques/<slug:slug>/eliminar/", views.admin_eliminar_parque, name="admin_eliminar_parque"),
    path("fila-admin/reservaciones/", views.admin_reservaciones, name="admin_reservaciones"),
    path("fila-admin/reservaciones/<str:folio>/", views.admin_detalle_reservacion, name="admin_detalle_reservacion"),
    path("fila-admin/disponibilidad/", views.admin_disponibilidad, name="admin_disponibilidad"),
    path("fila-admin/contacto/", views.admin_contacto, name="admin_contacto"),
    path("logout/", views.logout_view, name="logout"),
]
