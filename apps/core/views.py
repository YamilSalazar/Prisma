from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.utils.http import url_has_allowed_host_and_scheme

import calendar as _calendar
import datetime as _dt
import random as _random

from django.contrib.auth.decorators import login_required

from .forms import RegisterForm
from .models import (
    ContactoFestival,
    Disponibilidad,
    Parque,
    Reservacion,
    Resena,
)

# Meses en español para etiquetas del calendario de reservación
_MESES_ES = [
    "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio",
    "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre",
]
_TEMPORADA_INICIO = _dt.date(2026, 6, 1)
_TEMPORADA_FIN = _dt.date(2026, 8, 31)


def _calcular_costos(precio, noches):
    """Desglose de costos coherente con el comando seed."""
    subtotal = precio * noches
    servicio = round(subtotal * 0.05)
    impuestos = round((subtotal + servicio) * 0.16)
    total = subtotal + servicio + impuestos
    return subtotal, servicio, impuestos, total


def _build_calendar(parque, year, month, selected_iso=None):
    """Construye la malla del calendario para un parque/mes desde Disponibilidad.

    Devuelve una lista plana de celdas (para el grid `.calendar-days`):
      None                → celda vacía (días de otro mes)
      dict {day, date, estado, blocked, selected} → día del mes
    """
    disp = {
        d.fecha: d
        for d in Disponibilidad.objects.filter(
            parque=parque, fecha__year=year, fecha__month=month
        )
    }
    cal = _calendar.Calendar(firstweekday=0)  # 0 = lunes
    celdas = []
    for semana in cal.monthdatescalendar(year, month):
        for fecha in semana:
            if fecha.month != month:
                celdas.append(None)
                continue
            registro = disp.get(fecha)
            estado = registro.estado if registro else "blocked"
            blocked = estado in ("full", "blocked") or registro is None
            celdas.append({
                "day": fecha.day,
                "date": fecha.isoformat(),
                "estado": estado,
                "blocked": blocked,
                "selected": selected_iso == fecha.isoformat(),
            })
    return celdas


def _build_admin_calendar(parque, year, month):
    """Como `_build_calendar`, pero todas las celdas son editables y exponen
    cupos/reservadas para el modal de gestión de disponibilidad del admin."""
    disp = {
        d.fecha: d
        for d in Disponibilidad.objects.filter(
            parque=parque, fecha__year=year, fecha__month=month
        )
    }
    cal = _calendar.Calendar(firstweekday=0)
    celdas = []
    for semana in cal.monthdatescalendar(year, month):
        for fecha in semana:
            if fecha.month != month:
                celdas.append(None)
                continue
            d = disp.get(fecha)
            es_finde = fecha.weekday() >= 4
            celdas.append({
                "day": fecha.day,
                "date": fecha.isoformat(),
                "estado": d.estado if d else "available",
                "weekend": es_finde,
                "cupo_cabanas": d.cupo_cabanas if d else parque.capacidad_cabanas,
                "cupo_camping": d.cupo_camping if d else parque.capacidad_camping,
                "reservadas_cabanas": d.reservadas_cabanas if d else 0,
                "reservadas_camping": d.reservadas_camping if d else 0,
                "disp_cabanas": d.disponibles_cabanas if d else parque.capacidad_cabanas,
                "disp_camping": d.disponibles_camping if d else parque.capacidad_camping,
            })
    return celdas


def _context(active="home", title="Festival Internacional de las Luciérnagas 2026", **extra):
    parks = list(
        Parque.objects.filter(activo=True).prefetch_related("amenidades", "resenas")
    )
    context = {
        "active": active,
        "page_title": title,
        "parks": parks,
        "featured_parks": parks[:3],
    }
    context.update(extra)
    return context


def home(request):
    return render(request, "core/home.html", _context("home"))


import folium
from django.urls import reverse
from folium.features import DivIcon

# CSS inyectado para que los estilos existan dentro del iframe de Folium
FOLIUM_CUSTOM_CSS = """
<script src="https://unpkg.com/@phosphor-icons/web"></script>
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');

html,
body,
.folium-map,
.leaflet-container {
    width: 100% !important;
    height: 100% !important;
    min-height: 100% !important;
}

body {
    margin: 0 !important;
}

.leaflet-container::after {
    content: "";
    position: absolute;
    inset: 0;
    z-index: 400;
    background: transparent;
    pointer-events: none;
}
 
/* Estilos Bioluminiscentes para el Tooltip Nativo de Folium */
.leaflet-tooltip {
    background-color: #0f1a0d !important;
    border: 1px solid #c8975a !important;
    box-shadow: 0 6px 18px rgba(15, 26, 13, 0.72), 0 0 10px rgba(200, 151, 90, 0.18) !important;
    color: #f0ede5 !important;
    border-radius: 4px !important;
    padding: 0 !important;
}
.leaflet-tooltip-top:before, .leaflet-tooltip-bottom:before, .leaflet-tooltip-left:before, .leaflet-tooltip-right:before {
    display: none !important;
}
 
.fp-pin {
    display: flex;
    flex-direction: column;
    align-items: center;
    cursor: pointer;
    font-family: 'Montserrat', sans-serif;
    margin-top: -66px;
    margin-left: -18px;
    width: 36px;
    transition: transform 0.2s ease;
}
.fp-pin:hover { transform: translateY(-2px) scale(1.08); }
.fp-price {
    background-color: rgba(15, 26, 13, 0.9);
    color: #d9aa6e;
    border: 1px solid rgba(200, 151, 90, 0.45);
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
    margin-bottom: 4px;
    white-space: nowrap;
    transition: all 0.2s ease;
}
.fp-pin svg path { fill: #B8552A; transition: fill 0.2s ease; }
.fp-pin:hover .fp-price { background-color: #c8975a; color: #0f1a0d; }
.fp-pin:hover svg path { fill: #d96838; }
</style>
<script>
window.addEventListener("load", function () {
    function resizeFoliumMaps() {
        Object.keys(window).forEach(function (key) {
            if (key.indexOf("map_") === 0 && window[key] && window[key].invalidateSize) {
                window[key].invalidateSize(true);
            }
        });
    }
    setTimeout(resizeFoliumMaps, 100);
    setTimeout(resizeFoliumMaps, 450);
    window.addEventListener("resize", resizeFoliumMaps);
});
</script>
"""

def map_view(request):
    parks = list(Parque.objects.filter(activo=True).prefetch_related("resenas"))

    # Calcular centro promedio (Nanacamilpa)
    center_lat = sum(p.lat for p in parks) / len(parks)
    center_lng = sum(p.lng for p in parks) / len(parks)

    # Crear mapa con estilo oscuro (CartoDB dark_matter)
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=14,
        tiles="OpenStreetMap",
        width="100%",
        height="100%",
        min_zoom=12,
    )
    bounds = [
        [min(p.lat for p in parks), min(p.lng for p in parks)],
        [max(p.lat for p in parks), max(p.lng for p in parks)],
    ]
    m.fit_bounds(bounds, padding=(48, 48))

    m.get_root().html.add_child(folium.Element(FOLIUM_CUSTOM_CSS))

    # Agregar marcadores interactivos bioluminiscentes
    for park in parks:
        park_url = reverse("core:park_detail", args=[park.slug])

        # HTML personalizado del pin con la nueva estética de luciérnaga
        marker_html = f"""
        <div onclick="window.parent.location.href='{park_url}'" class="fp-pin">
            <div class="fp-price">${park.price}</div>
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="42"
                 style="filter:drop-shadow(0 1px 2px rgba(0,0,0,0.32))">
                <path fill-rule="evenodd"
                      stroke="#0F1A0D" stroke-width="1.0" stroke-linejoin="round"
                      d="M12,2C8.13,2 5,5.13 5,9c0,5.25 7,13 7,13s7-7.75 7-13C19,5.13 15.87,2 12,2Z M9.5,9a2.5,2.5 0 1,0 5,0a2.5,2.5 0 1,0-5,0Z"/>
            </svg>
        </div>
        """

        # Mini-tarjeta de detalles para el Tooltip al pasar el cursor
        tooltip_html = f"""
        <div style="font-family: 'Montserrat', sans-serif; padding: 6px 8px; min-width: 220px; max-width: 280px;">
            <div style="font-weight: 800; font-size: 13px; color: #f0ede5; margin-bottom: 5px;">{park.name}</div>
            <div style="font-size: 11px; color: rgba(240, 237, 229, 0.8); line-height: 1.45;">
                <span style="color: #c8975a; font-weight: bold;"><i class="ph-fill ph-star"></i> {park.rating}</span>
                <span style="color: #8a9a8c;">({park.reviews} reseñas)</span><br>
                <b>{park.type}</b> • <i class="ph ph-person" style="color:#f0ede5; font-size:13px; vertical-align:middle;"></i> {park.capacity.split()[0]}<br>
                <div style="margin-top: 4px; font-size: 10px; color: #8a9a8c; display: flex; align-items: flex-start; gap: 4px;">
                    <i class="ph ph-map-trifold" style="font-size: 12px; margin-top: 1px; flex: 0 0 auto;"></i> <span style="white-space: normal;">{park.address}</span>
                </div>
            </div>
        </div>
        """

        folium.Marker(
            location=[park.lat, park.lng],
            tooltip=tooltip_html,
            icon=DivIcon(html=marker_html)
        ).add_to(m)

    # Obtener representación HTML del mapa
    map_html = m._repr_html_()

    return render(request, "core/map.html", _context("map", map_html=map_html, hide_footer=True, full_bleed=True))


def park_list(request):
    return render(request, "core/park_list.html", _context("park_list"))


def park_detail(request, slug):
    park = get_object_or_404(
        Parque.objects.prefetch_related("amenidades", "resenas"), slug=slug
    )

    # Crear mini-mapa centrado en este parque específico
    m = folium.Map(
        location=[park.lat, park.lng],
        zoom_start=15,
        tiles="OpenStreetMap",
        zoom_control=True
    )

    # Inyectar estilos bioluminiscentes
    m.get_root().html.add_child(folium.Element(FOLIUM_CUSTOM_CSS))

    # Marcador único para el detalle (sin redirección clic ya que estamos en la página)
    marker_html = f"""
    <div class="fp-pin" style="cursor: default;">
        <div class="fp-price">${park.price}</div>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="42"
             style="filter:drop-shadow(0 1px 2px rgba(0,0,0,0.32))">
            <path fill-rule="evenodd"
                  stroke="#0F1A0D" stroke-width="1.0" stroke-linejoin="round"
                  d="M12,2C8.13,2 5,5.13 5,9c0,5.25 7,13 7,13s7-7.75 7-13C19,5.13 15.87,2 12,2Z M9.5,9a2.5,2.5 0 1,0 5,0a2.5,2.5 0 1,0-5,0Z"/>
        </svg>
    </div>
    """
    
    folium.Marker(
        location=[park.lat, park.lng],
        tooltip=park.name,
        icon=DivIcon(html=marker_html)
    ).add_to(m)

    map_html = m._repr_html_()

    return render(request, "core/park_detail.html", _context("park_list", selected_park=park, map_html=map_html))


def login_view(request):

    if request.method == "POST":

        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(
            request,
            username=email,
            password=password
        )

        if user is not None:

            login(request, user)

            messages.success(
                request,
                "Inicio de sesión exitoso."
            )

            # Respetar ?next= (p. ej. al pulsar "Reservar" sin sesión)
            next_url = request.POST.get("next") or request.GET.get("next")
            if next_url and url_has_allowed_host_and_scheme(
                next_url, allowed_hosts={request.get_host()}, require_https=request.is_secure()
            ):
                return redirect(next_url)

            if user.is_staff:
                return redirect('/fila-admin/')

            return redirect("core:home")

        messages.error(
            request,
            "Correo o contraseña incorrectos."
        )

    return render(
        request,
        "core/auth/login.html",
        _context("login")
    )


def register(request):

    if request.method == "POST":

        form = RegisterForm(request.POST)

        if form.is_valid():
            form.save()

            messages.success(
                request,
                "Cuenta creada correctamente."
            )

            return redirect("core:login")

    else:
        form = RegisterForm()

    return render(
        request,
        "core/auth/register.html",
        _context(
            "register",
            form=form
        )
    )

def logout_view(request):
    logout(request)
    messages.success(request, "Sesión cerrada correctamente.")
    return redirect("core:home")


def set_idioma(request, code):
    """Cambia el idioma de la interfaz (ES/EN) y vuelve a la página previa."""
    from .translations import LANGS

    if code in LANGS:
        request.session["idioma"] = code
        if request.user.is_authenticated:
            request.user.idioma = code
            request.user.save(update_fields=["idioma"])

    destino = request.META.get("HTTP_REFERER") or "/"
    return redirect(destino)

def password_reset(request):
    return render(request, "core/auth/password_reset.html", _context("password_reset"))

def password_reset_sent(request):
    return render(request, "core/auth/password_reset_sent.html", _context("login"))

def password_reset_confirm(request):
    return render(request, "core/auth/password_reset_confirm.html", _context("login"))


@login_required
def booking_details(request):
    """Paso 1: elegir parque, fecha de entrada (calendario real), noches y personas."""
    parques = list(Parque.objects.filter(activo=True))
    booking = request.session.get("booking", {})

    # Parque seleccionado: query ?parque= → sesión → primero
    slug = request.GET.get("parque") or booking.get("parque")
    parque = next((p for p in parques if p.slug == slug), parques[0] if parques else None)

    if request.method == "POST":
        post_slug = request.POST.get("parque")
        parque = next((p for p in parques if p.slug == post_slug), parque)
        fecha_entrada = request.POST.get("fecha_entrada") or ""
        try:
            noches = max(1, int(request.POST.get("noches", 2)))
            personas = max(1, int(request.POST.get("personas", 2)))
        except (TypeError, ValueError):
            noches, personas = 2, 2

        if parque and fecha_entrada:
            request.session["booking"] = {
                "parque": parque.slug,
                "fecha_entrada": fecha_entrada,
                "noches": noches,
                "personas": personas,
                "tipo": request.POST.get("tipo", parque.tipo),
            }
            return redirect("core:booking_summary")
        messages.error(request, "Selecciona una fecha de entrada disponible para continuar.")

    # Mes a mostrar: ?mes=YYYY-MM → temporada por defecto (junio 2026)
    mes_param = request.GET.get("mes", "")
    try:
        year, month = (int(x) for x in mes_param.split("-"))
        _dt.date(year, month, 1)
    except (ValueError, AttributeError):
        year, month = 2026, 6

    selected_iso = booking.get("fecha_entrada")
    celdas = _build_calendar(parque, year, month, selected_iso) if parque else []

    primero = _dt.date(year, month, 1)
    mes_prev = (primero - _dt.timedelta(days=1)).replace(day=1)
    mes_next = (primero + _dt.timedelta(days=31)).replace(day=1)

    ctx = _context(
        "booking",
        booking_parque=parque,
        calendar_cells=celdas,
        calendar_label=f"{_MESES_ES[month - 1]} {year}",
        mes_prev=mes_prev.strftime("%Y-%m") if mes_prev >= _TEMPORADA_INICIO.replace(day=1) else "",
        mes_next=mes_next.strftime("%Y-%m") if mes_next <= _TEMPORADA_FIN else "",
        sel_noches=booking.get("noches", 2),
        sel_personas=booking.get("personas", 2),
        sel_fecha=selected_iso or "",
    )
    return render(request, "core/booking/details.html", ctx)


def _booking_or_redirect(request):
    """Devuelve (booking, parque) desde la sesión o None si falta info."""
    booking = request.session.get("booking")
    if not booking:
        return None, None
    parque = Parque.objects.filter(slug=booking.get("parque")).first()
    return (booking, parque) if parque else (None, None)


@login_required
def booking_summary(request):
    """Paso 2: resumen con desglose de costo real."""
    booking, parque = _booking_or_redirect(request)
    if not booking:
        messages.error(request, "Empieza eligiendo un parque y una fecha.")
        return redirect("core:park_list")

    entrada = _dt.date.fromisoformat(booking["fecha_entrada"])
    salida = entrada + _dt.timedelta(days=booking["noches"])
    subtotal, servicio, impuestos, total = _calcular_costos(parque.precio, booking["noches"])

    ctx = _context(
        "booking",
        booking=booking, booking_parque=parque,
        entrada=entrada, salida=salida,
        subtotal=subtotal, servicio=servicio, impuestos=impuestos, total=total,
    )
    return render(request, "core/booking/summary.html", ctx)


@login_required
def booking_payment(request):
    """Paso 3: pago. Al confirmar crea la Reservacion real."""
    booking, parque = _booking_or_redirect(request)
    if not booking:
        messages.error(request, "Empieza eligiendo un parque y una fecha.")
        return redirect("core:park_list")

    entrada = _dt.date.fromisoformat(booking["fecha_entrada"])
    salida = entrada + _dt.timedelta(days=booking["noches"])
    subtotal, servicio, impuestos, total = _calcular_costos(parque.precio, booking["noches"])

    if request.method == "POST":
        last4 = "".join(c for c in request.POST.get("numero", "") if c.isdigit())[-4:] or "0000"
        folio = f"FIL-2026-{_random.randint(10000, 99999)}"
        while Reservacion.objects.filter(folio=folio).exists():
            folio = f"FIL-2026-{_random.randint(10000, 99999)}"

        reserva = Reservacion.objects.create(
            folio=folio,
            usuario=request.user,
            parque=parque,
            tipo_hospedaje=booking.get("tipo", parque.tipo),
            fecha_entrada=entrada,
            fecha_salida=salida,
            noches=booking["noches"],
            personas=booking["personas"],
            subtotal=subtotal, servicio=servicio, impuestos=impuestos, total=total,
            estado="activa",
            metodo_pago_marca="Visa",
            metodo_pago_last4=last4,
        )

        # Reflejar la ocupación en disponibilidad para esa fecha
        disp = Disponibilidad.objects.filter(parque=parque, fecha=entrada).first()
        if disp:
            if booking.get("tipo") == "Camping":
                disp.reservadas_camping = min(disp.reservadas_camping + 1, disp.cupo_camping)
            else:
                disp.reservadas_cabanas = min(disp.reservadas_cabanas + 1, disp.cupo_cabanas)
            disp.save()

        request.session.pop("booking", None)
        request.session["ultima_reserva"] = reserva.id
        return redirect("core:booking_confirmation")

    ctx = _context(
        "booking",
        booking=booking, booking_parque=parque,
        entrada=entrada, salida=salida,
        subtotal=subtotal, servicio=servicio, impuestos=impuestos, total=total,
    )
    return render(request, "core/booking/payment.html", ctx)


@login_required
def booking_confirmation(request):
    """Paso 4: confirmación con la reservación recién creada."""
    reserva_id = request.session.get("ultima_reserva")
    reserva = (
        Reservacion.objects.filter(id=reserva_id, usuario=request.user).first()
        if reserva_id else None
    )
    if not reserva:
        return redirect("core:reservations")
    return render(
        request, "core/booking/confirmation.html",
        _context("booking", reserva=reserva),
    )


@login_required
def reservations(request):
    qs = request.user.reservaciones.select_related("parque")
    activas = [r for r in qs if r.estado == "activa"]
    historial = [r for r in qs if r.estado != "activa"]
    return render(
        request, "core/account/reservations.html",
        _context("reservations", activas=activas, historial=historial),
    )


@login_required
def cancelar_reservacion(request, folio):
    if request.method == "POST":
        reserva = Reservacion.objects.filter(folio=folio, usuario=request.user).first()
        if reserva and reserva.estado == "activa":
            reserva.estado = "cancelada"
            reserva.save(update_fields=["estado"])
            messages.success(request, "Tu reservación fue cancelada y se procesará el reembolso.")
    return redirect("core:reservations")


@login_required
def account(request):
    return render(request, "core/account/account.html", _context("account"))


@login_required
def change_password(request):
    return render(request, "core/account/change_password.html", _context("account"))


@login_required
def crear_resena(request):
    """Crea una reseña para un parque (modal 'Calificar parque')."""
    if request.method == "POST":
        slug = request.POST.get("parque")
        parque = Parque.objects.filter(slug=slug).first()
        try:
            rating = int(request.POST.get("rating", 0))
        except (TypeError, ValueError):
            rating = 0

        if parque and 1 <= rating <= 5:
            Resena.objects.create(
                parque=parque,
                usuario=request.user,
                autor_nombre=request.user.get_full_name() or request.user.email,
                rating=rating,
                comentario=request.POST.get("comentario", "").strip(),
                verificada=True,
            )
            messages.success(request, "¡Gracias! Tu reseña se publicó correctamente.")
        else:
            messages.error(request, "No se pudo registrar la reseña. Selecciona una calificación.")

    return redirect("core:reservations")


# ──────────────────────────────────────────────────────────────────
# Admin views
# Protegidas con @staff_member_required: sólo usuarios con is_staff=True
# pueden acceder. En caso contrario redirigen a /login/?next=<url>.
# ──────────────────────────────────────────────────────────────────

from django.contrib.admin.views.decorators import staff_member_required


def _admin_context(active_section="panel", **extra):
    """Contexto base para todas las vistas del panel admin."""
    context = {
        "active_section": active_section,
        "parks": list(Parque.objects.prefetch_related("amenidades")),
    }
    context.update(extra)
    return context


@staff_member_required(login_url="/login/")
def admin_panel(request):
    reservaciones = Reservacion.objects.all()
    activas = reservaciones.filter(estado="activa").count()
    ingresos = sum(
        r.total for r in reservaciones.exclude(estado="cancelada")
    )

    # Ocupación promedio sobre la disponibilidad sembrada
    disp = Disponibilidad.objects.all()
    cupo = sum(d.cupo_cabanas + d.cupo_camping for d in disp) or 1
    ocupadas = sum(d.reservadas_cabanas + d.reservadas_camping for d in disp)
    ocupacion = round(ocupadas / cupo * 100)

    parques_activos = Parque.objects.filter(activo=True).count()
    parques_total = Parque.objects.count()
    stats = {
        "activas": activas,
        "ocupacion": ocupacion,
        "parques_activos": parques_activos,
        "parques_total": parques_total,
        "parques_inactivos": parques_total - parques_activos,
        "ingresos": ingresos,
    }
    ultimas = reservaciones.select_related("parque", "usuario").order_by("-creada")[:5]
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("panel", stats=stats, ultimas=ultimas),
    )


@staff_member_required(login_url="/login/")
def admin_parques(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("parques"))


def _parque_from_post(request, parque):
    """Asigna a `parque` los campos enviados desde el formulario admin."""
    from django.utils.text import slugify

    parque.nombre = request.POST.get("nombre", parque.nombre).strip()
    parque.direccion = request.POST.get("direccion", parque.direccion).strip()
    parque.tipo = request.POST.get("tipo", parque.tipo or "Cabaña")
    parque.precio = int(request.POST.get("precio") or parque.precio or 0)
    parque.capacidad_personas = int(request.POST.get("capacidad_personas") or parque.capacidad_personas or 4)
    parque.capacidad_cabanas = int(request.POST.get("capacidad_cabanas") or 0)
    parque.capacidad_camping = int(request.POST.get("capacidad_camping") or 0)
    parque.activo = request.POST.get("activo", "on") == "on"
    if not parque.slug:
        parque.slug = slugify(parque.nombre) or "parque"
    if not parque.carpeta_imagenes:
        parque.carpeta_imagenes = request.POST.get("carpeta_imagenes") or "bosque_magico"
    parque.save()

    # Amenidades desde los checkboxes (name="amenidades")
    labels = request.POST.getlist("amenidades")
    if labels:
        parque.amenidades.all().delete()
        for label in labels:
            parque.amenidades.create(label=label)
    return parque


@staff_member_required(login_url="/login/")
def admin_agregar_parque(request):
    if request.method == "POST":
        try:
            parque = _parque_from_post(request, Parque())
            messages.success(request, f"Parque «{parque.nombre}» creado correctamente.")
            return redirect("core:admin_parques")
        except (ValueError, TypeError):
            messages.error(request, "Revisa los datos del formulario.")
    return render(request, "core/admin/admin-prisma.html", _admin_context("agregar"))


@staff_member_required(login_url="/login/")
def admin_editar_parque(request, slug):
    park = get_object_or_404(Parque, slug=slug)
    if request.method == "POST":
        try:
            _parque_from_post(request, park)
            messages.success(request, "Cambios guardados.")
            return redirect("core:admin_parques")
        except (ValueError, TypeError):
            messages.error(request, "Revisa los datos del formulario.")
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("editar", selected_park=park),
    )


@staff_member_required(login_url="/login/")
def admin_eliminar_parque(request, slug):
    from django.db.models import ProtectedError

    park = get_object_or_404(Parque, slug=slug)
    if request.method == "POST":
        try:
            nombre = park.nombre
            park.delete()
            messages.success(request, f"Parque «{nombre}» eliminado.")
        except ProtectedError:
            park.activo = False
            park.save(update_fields=["activo"])
            messages.success(
                request,
                "El parque tiene reservaciones; se marcó como inactivo en lugar de eliminarse.",
            )
        return redirect("core:admin_parques")
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("eliminar", selected_park=park),
    )


@staff_member_required(login_url="/login/")
def admin_reservaciones(request):
    reservaciones = Reservacion.objects.select_related("parque", "usuario").order_by("-creada")
    stats = {
        "total": reservaciones.count(),
        "activas": reservaciones.filter(estado="activa").count(),
        "completadas": reservaciones.filter(estado="completada").count(),
        "canceladas": reservaciones.filter(estado="cancelada").count(),
    }
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("reservaciones", reservaciones=reservaciones, stats=stats),
    )


@staff_member_required(login_url="/login/")
def admin_detalle_reservacion(request, folio):
    reserva = get_object_or_404(
        Reservacion.objects.select_related("parque", "usuario"), folio=folio
    )
    if request.method == "POST":
        nuevo_estado = request.POST.get("estado")
        if nuevo_estado in dict(Reservacion.ESTADOS):
            reserva.estado = nuevo_estado
            reserva.save(update_fields=["estado"])
            messages.success(request, "Estado de la reservación actualizado.")
        return redirect("core:admin_detalle_reservacion", folio=folio)
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("detalle", folio=folio, reserva=reserva),
    )


@staff_member_required(login_url="/login/")
def admin_disponibilidad(request):
    parques = list(Parque.objects.all())

    if request.method == "POST":
        slug = request.POST.get("parque")
        fecha_iso = request.POST.get("fecha")
        parque = next((p for p in parques if p.slug == slug), None)
        if parque and fecha_iso:
            fecha = _dt.date.fromisoformat(fecha_iso)
            disp, _ = Disponibilidad.objects.get_or_create(parque=parque, fecha=fecha)
            disp.cupo_cabanas = int(request.POST.get("cupo_cabanas") or disp.cupo_cabanas)
            disp.cupo_camping = int(request.POST.get("cupo_camping") or disp.cupo_camping)
            if request.POST.get("bloquear") == "on":
                disp.estado = "blocked"
            else:
                libres = disp.disponibles_cabanas + disp.disponibles_camping
                total = max(disp.cupo_cabanas + disp.cupo_camping, 1)
                disp.estado = "full" if libres == 0 else ("low" if libres / total <= 0.2 else "available")
            disp.save()
            messages.success(request, "Disponibilidad actualizada.")
        return redirect(f"{reverse('core:admin_disponibilidad')}?parque={slug}")

    slug = request.GET.get("parque") or (parques[0].slug if parques else "")
    parque = next((p for p in parques if p.slug == slug), parques[0] if parques else None)

    mes_param = request.GET.get("mes", "")
    try:
        year, month = (int(x) for x in mes_param.split("-"))
        _dt.date(year, month, 1)
    except (ValueError, AttributeError):
        year, month = 2026, 7

    celdas = _build_admin_calendar(parque, year, month) if parque else []
    primero = _dt.date(year, month, 1)
    mes_prev = (primero - _dt.timedelta(days=1)).replace(day=1)
    mes_next = (primero + _dt.timedelta(days=31)).replace(day=1)

    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context(
            "disponibilidad",
            disp_parque=parque,
            disp_cells=celdas,
            disp_label=f"{_MESES_ES[month - 1]} {year}",
            disp_mes_prev=mes_prev.strftime("%Y-%m") if mes_prev >= _TEMPORADA_INICIO.replace(day=1) else "",
            disp_mes_next=mes_next.strftime("%Y-%m") if mes_next <= _TEMPORADA_FIN else "",
        ),
    )


@staff_member_required(login_url="/login/")
def admin_contacto(request):
    contacto = ContactoFestival.get_solo()

    if request.method == "POST":
        contacto.email = request.POST.get("email", contacto.email)
        contacto.telefono = request.POST.get("telefono", contacto.telefono)
        contacto.horario = request.POST.get("horario", contacto.horario)
        contacto.fechas_festival = request.POST.get("fechas_festival", contacto.fechas_festival)
        contacto.instagram = request.POST.get("instagram", contacto.instagram)
        contacto.web = request.POST.get("web", contacto.web)
        contacto.twitter = request.POST.get("twitter", contacto.twitter)
        contacto.youtube = request.POST.get("youtube", contacto.youtube)
        contacto.mensaje_soporte = request.POST.get("mensaje_soporte", contacto.mensaje_soporte)
        contacto.save()
        messages.success(request, "Datos de contacto actualizados.")
        return redirect("core:admin_contacto")

    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("contacto", contacto=contacto),
    )

