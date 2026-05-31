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

def map_view(request):
    # Calcular centro promedio (Nanacamilpa)
    center_lat = sum(p["lat"] for p in PARKS) / len(PARKS)
    center_lng = sum(p["lng"] for p in PARKS) / len(PARKS)

    # Crear mapa con estilo oscuro (CartoDB dark_matter)
    m = folium.Map(
        location=[center_lat, center_lng],
        zoom_start=13,
        tiles="CartoDB dark_matter"
    )

    # CSS inyectado para que los estilos existan dentro del iframe de Folium
    custom_css = """
    <script src="https://unpkg.com/@phosphor-icons/web"></script>
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700&display=swap');
    
    /* Estilos Bioluminiscentes para el Tooltip Nativo de Folium */
    .leaflet-tooltip {
        background-color: #0f1a0d !important;
        border: 1px solid #c8975a !important;
        box-shadow: 0 8px 24px rgba(15, 26, 13, 0.9), 0 0 14px rgba(255, 213, 79, 0.25), inset 0 0 12px rgba(200, 151, 90, 0.15) !important;
        color: #f0ede5 !important;
        border-radius: 4px !important;
        padding: 0 !important;
    }
    .leaflet-tooltip-top:before, .leaflet-tooltip-bottom:before, .leaflet-tooltip-left:before, .leaflet-tooltip-right:before {
        display: none !important;
    }
    
    .firefly-pin {
        display: flex;
        flex-direction: column;
        align-items: center;
        cursor: pointer;
        font-family: 'Montserrat', sans-serif;
        margin-top: -35px; 
        margin-left: -30px;
        width: 60px;
    }
    .firefly-price {
        background-color: #142a19;
        color: #ffd54f;
        border: 1px solid #ffd54f;
        padding: 4px 6px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: bold;
        margin-bottom: 6px;
        box-shadow: 0 0 10px rgba(255, 213, 79, 0.4);
        transition: all 0.3s ease;
    }
    .firefly-orb {
        width: 14px;
        height: 14px;
        background-color: #ffe666;
        border-radius: 50%;
        box-shadow: 0 0 15px #fbd341, 0 0 30px #e6a832;
        animation: pulse 1.5s infinite alternate;
        transition: all 0.3s ease;
    }
    .firefly-pin:hover .firefly-price {
        background-color: #ffd54f;
        color: #142a19;
        box-shadow: 0 0 20px rgba(255, 213, 79, 0.8);
    }
    .firefly-pin:hover .firefly-orb {
        box-shadow: 0 0 25px #ffe666, 0 0 45px #fbd341;
        transform: scale(1.3);
    }
    @keyframes pulse {
        0% { transform: scale(0.85); opacity: 0.8; box-shadow: 0 0 8px #fbd341; }
        100% { transform: scale(1.15); opacity: 1; box-shadow: 0 0 18px #ffe666, 0 0 25px #fbd341; }
    }
    </style>
    """
    m.get_root().html.add_child(folium.Element(custom_css))

    # Agregar marcadores interactivos bioluminiscentes
    for park in PARKS:
        park_url = reverse("core:park_detail", args=[park["slug"]])
        
        # HTML personalizado del pin con la nueva estética de luciérnaga
        marker_html = f"""
        <div onclick="window.parent.location.href='{park_url}'" class="firefly-pin">
            <div class="firefly-price">${park['price']}</div>
            <div class="firefly-orb"></div>
        </div>
        """
        
        # Mini-tarjeta de detalles para el Tooltip al pasar el cursor
        tooltip_html = f"""
        <div style="font-family: 'Montserrat', sans-serif; padding: 6px 8px; min-width: 170px;">
            <div style="font-weight: 800; font-size: 14px; color: #f0ede5; margin-bottom: 6px;">{park['name']}</div>
            <div style="font-size: 12px; color: rgba(240, 237, 229, 0.8); line-height: 1.5;">
                <span style="color: #c8975a; font-weight: bold;"><i class="ph-fill ph-star"></i> {park['rating']}</span> 
                <span style="color: #8a9a8c;">({park['reviews']} reseñas)</span><br>
                <b>{park['type']}</b> • {park['capacity']}<br>
                <div style="margin-top: 4px; font-size: 10px; color: #8a9a8c; display: flex; align-items: flex-start; gap: 4px;">
                    <i class="ph ph-map-trifold" style="font-size: 14px; margin-top: 1px;"></i> <span>{park['address']}</span>
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

    return render(request, "core/map.html", _context("map", hide_footer=True, map_html=map_html))


def park_list(request):
    return render(request, "core/park_list.html", _context("park_list"))


def park_detail(request, slug):
    park = next((item for item in PARKS if item["slug"] == slug), PARKS[2])
    return render(request, "core/park_detail.html", _context("park_list", selected_park=park))


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
