from django.shortcuts import render, redirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 

from .forms import RegisterForm 


PARKS = [
    {
        "slug": "santuario-piedra-canteada",
        "name": "Santuario Piedra Canteada",
        "type": "Cabaña",
        "price": 1850,
        "capacity": "4 pers",
        "rating": 4.9,
        "reviews": 342,
        "amenities": ["Chimenea", "Baño privado", "Estacionamiento", "Restaurante"],
        "address": "Camino a San Felipe Hidalgo Km 4.5, Nanacamilpa",
        "lat": 19.462312,
        "lng": -98.568421,
    },
    {
        "slug": "canto-del-bosque",
        "name": "Canto del Bosque",
        "type": "Camping",
        "price": 750,
        "capacity": "6 pers",
        "rating": 4.7,
        "reviews": 215,
        "amenities": ["Fogata", "Baños comunes", "Estacionamiento", "Guía certificado"],
        "address": "San Felipe Hidalgo s/n, Nanacamilpa, Tlaxcala",
        "lat": 19.458045,
        "lng": -98.542012,
    },
    {
        "slug": "santuario-el-salto",
        "name": "Santuario El Salto",
        "type": "Cabaña",
        "price": 1420,
        "capacity": "2 pers",
        "rating": 4.8,
        "reviews": 128,
        "amenities": ["Vista panorámica", "Baño privado", "Desayuno"],
        "address": "Zona Boscosa San Felipe Hidalgo, Lote 12",
        "lat": 19.481234,
        "lng": -98.529876,
    },
    {
        "slug": "bosque-magico",
        "name": "Bosque Mágico",
        "type": "Cabaña",
        "price": 1200,
        "capacity": "4 pers",
        "rating": 4.6,
        "reviews": 92,
        "amenities": ["Cocineta", "Terraza", "Baño privado"],
        "address": "Camino Forestal Nanacamilpa, Sendero 4",
        "lat": 19.445089,
        "lng": -98.551045,
    },
    {
        "slug": "santuario-las-minas",
        "name": "Santuario Las Minas",
        "type": "Cabaña",
        "price": 1580,
        "capacity": "6 pers",
        "rating": 4.7,
        "reviews": 156,
        "amenities": ["Chimenea", "Cocina equipada", "Jardín", "Senderismo"],
        "address": "Antigua Zona Minera, San Felipe Hidalgo",
        "lat": 19.492567,
        "lng": -98.538012,
    },
    {
        "slug": "rancho-el-ciervo",
        "name": "Santuario Rancho El Ciervo",
        "type": "Camping",
        "price": 540,
        "capacity": "4 pers",
        "rating": 4.5,
        "reviews": 84,
        "amenities": ["Asadores", "Baños comunes", "Área recreativa"],
        "address": "Km 8 Carretera Nanacamilpa-Mazapa",
        "lat": 19.470512,
        "lng": -98.555567,
    },
]


def _amenity_icon(label):
    import unicodedata

    normalized = unicodedata.normalize("NFKD", label.lower())
    normalized = "".join(char for char in normalized if not unicodedata.combining(char))
    if "privado" in normalized:
        return "ph-bathtub"
    if "bano" in normalized or "banos" in normalized:
        return "ph-shower"
    if "vista" in normalized:
        return "ph-mountains"
    if "jardin" in normalized:
        return "ph-plant"
    if "chimenea" in normalized:
        return "ph-fire"
    if "estacionamiento" in normalized:
        return "ph-car"
    if "wi-fi" in normalized:
        return "ph-wifi-high"
    if "fogata" in normalized:
        return "ph-campfire"
    if "asadores" in normalized:
        return "ph-cooking-pot"
    if "desayuno" in normalized:
        return "ph-coffee"
    if "cocineta" in normalized or "cocina" in normalized:
        return "ph-cooking-pot"
    if "terraza" in normalized:
        return "ph-sun-horizon"
    return "ph-sparkle"


for park in PARKS:
    park["amenity_items"] = [
        {"label": amenity, "icon": _amenity_icon(amenity)}
        for amenity in park["amenities"]
    ]


def _context(active="home", title="Festival Internacional de las Luciérnagas 2026", **extra):
    context = {
        "active": active,
        "page_title": title,
        "parks": PARKS,
        "featured_parks": PARKS[:3],
        "selected_park": PARKS[2],
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
"""

def map_view(request):
    # Calcular centro promedio (Nanacamilpa)
    center_lat = sum(p["lat"] for p in PARKS) / len(PARKS)
    center_lng = sum(p["lng"] for p in PARKS) / len(PARKS)

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
        [min(p["lat"] for p in PARKS), min(p["lng"] for p in PARKS)],
        [max(p["lat"] for p in PARKS), max(p["lng"] for p in PARKS)],
    ]
    m.fit_bounds(bounds, padding=(48, 48))

    m.get_root().html.add_child(folium.Element(FOLIUM_CUSTOM_CSS))

    # Agregar marcadores interactivos bioluminiscentes
    for park in PARKS:
        park_url = reverse("core:park_detail", args=[park["slug"]])
        
        # HTML personalizado del pin con la nueva estética de luciérnaga
        marker_html = f"""
        <div onclick="window.parent.location.href='{park_url}'" class="fp-pin">
            <div class="fp-price">${park['price']}</div>
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
            <div style="font-weight: 800; font-size: 13px; color: #f0ede5; margin-bottom: 5px;">{park['name']}</div>
            <div style="font-size: 11px; color: rgba(240, 237, 229, 0.8); line-height: 1.45;">
                <span style="color: #c8975a; font-weight: bold;"><i class="ph-fill ph-star"></i> {park['rating']}</span> 
                <span style="color: #8a9a8c;">({park['reviews']} reseñas)</span><br>
                <b>{park['type']}</b> • <i class="ph ph-person" style="color:#f0ede5; font-size:13px; vertical-align:middle;"></i> {park['capacity'].split()[0]}<br>
                <div style="margin-top: 4px; font-size: 10px; color: #8a9a8c; display: flex; align-items: flex-start; gap: 4px;">
                    <i class="ph ph-map-trifold" style="font-size: 12px; margin-top: 1px; flex: 0 0 auto;"></i> <span style="white-space: normal;">{park['address']}</span>
                </div>
            </div>
        </div>
        """
        
        folium.Marker(
            location=[park["lat"], park["lng"]],
            tooltip=tooltip_html,
            icon=DivIcon(html=marker_html)
        ).add_to(m)

    # Obtener representación HTML del mapa
    map_html = m._repr_html_()

    return render(request, "core/map.html", _context("map", map_html=map_html, hide_footer=True, full_bleed=True))


def park_list(request):
    return render(request, "core/park_list.html", _context("park_list"))


def park_detail(request, slug):
    park = next((item for item in PARKS if item["slug"] == slug), PARKS[2])
    
    # Crear mini-mapa centrado en este parque específico
    m = folium.Map(
        location=[park["lat"], park["lng"]],
        zoom_start=15,
        tiles="OpenStreetMap",
        zoom_control=True
    )

    # Inyectar estilos bioluminiscentes
    m.get_root().html.add_child(folium.Element(FOLIUM_CUSTOM_CSS))

    # Marcador único para el detalle (sin redirección clic ya que estamos en la página)
    marker_html = f"""
    <div class="fp-pin" style="cursor: default;">
        <div class="fp-price">${park['price']}</div>
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="36" height="42"
             style="filter:drop-shadow(0 1px 2px rgba(0,0,0,0.32))">
            <path fill-rule="evenodd"
                  stroke="#0F1A0D" stroke-width="1.0" stroke-linejoin="round"
                  d="M12,2C8.13,2 5,5.13 5,9c0,5.25 7,13 7,13s7-7.75 7-13C19,5.13 15.87,2 12,2Z M9.5,9a2.5,2.5 0 1,0 5,0a2.5,2.5 0 1,0-5,0Z"/>
        </svg>
    </div>
    """
    
    folium.Marker(
        location=[park["lat"], park["lng"]],
        tooltip=park["name"],
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

def password_reset(request):
    return render(request, "core/auth/password_reset.html", _context("password_reset"))

def password_reset_sent(request):
    return render(request, "core/auth/password_reset_sent.html", _context("login"))

def password_reset_confirm(request):
    return render(request, "core/auth/password_reset_confirm.html", _context("login"))


def booking_details(request):
    return render(request, "core/booking/details.html", _context("booking"))


def booking_summary(request):
    return render(request, "core/booking/summary.html", _context("booking"))


def booking_payment(request):
    return render(request, "core/booking/payment.html", _context("booking"))


def booking_confirmation(request):
    return render(request, "core/booking/confirmation.html", _context("booking"))


def reservations(request):
    return render(request, "core/account/reservations.html", _context("reservations"))


def account(request):
    return render(request, "core/account/account.html", _context("account"))


def change_password(request):
    return render(request, "core/account/change_password.html", _context("account"))

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
        "parks": PARKS,
    }
    context.update(extra)
    return context


@staff_member_required(login_url="/login/")
def admin_panel(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("panel"))


@staff_member_required(login_url="/login/")
def admin_parques(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("parques"))


@staff_member_required(login_url="/login/")
def admin_agregar_parque(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("agregar"))


@staff_member_required(login_url="/login/")
def admin_editar_parque(request, slug):
    park = next((p for p in PARKS if p["slug"] == slug), None)
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("editar", selected_park=park),
    )


@staff_member_required(login_url="/login/")
def admin_eliminar_parque(request, slug):
    park = next((p for p in PARKS if p["slug"] == slug), None)
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("eliminar", selected_park=park),
    )


@staff_member_required(login_url="/login/")
def admin_reservaciones(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("reservaciones"))


@staff_member_required(login_url="/login/")
def admin_detalle_reservacion(request, folio):
    return render(
        request,
        "core/admin/admin-prisma.html",
        _admin_context("detalle", folio=folio),
    )


@staff_member_required(login_url="/login/")
def admin_disponibilidad(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("disponibilidad"))


@staff_member_required(login_url="/login/")
def admin_contacto(request):
    return render(request, "core/admin/admin-prisma.html", _admin_context("contacto"))

