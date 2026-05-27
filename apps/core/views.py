from django.shortcuts import render


PARKS = [
    {
        "slug": "cabanas-del-bosque",
        "name": "Cabañas del Bosque",
        "type": "Cabaña",
        "price": 1250,
        "capacity": "4 pers",
        "rating": 4.8,
        "reviews": 124,
        "amenities": ["Chimenea", "Baño privado", "Estacionamiento", "Wi-Fi"],
        "address": "Km 12 Carretera Sierra Norte",
    },
    {
        "slug": "camping-rio-verde",
        "name": "Camping Río Verde",
        "type": "Camping",
        "price": 680,
        "capacity": "6 pers",
        "rating": 4.5,
        "reviews": 87,
        "amenities": ["Fogata", "Baños comunes", "Estacionamiento"],
        "address": "Ribera del Río Verde s/n",
    },
    {
        "slug": "mirador-de-las-estrellas",
        "name": "Mirador de las Estrellas",
        "type": "Cabaña",
        "price": 1420,
        "capacity": "2 pers",
        "rating": 4.9,
        "reviews": 156,
        "amenities": ["Vista panorámica", "Baño privado", "Desayuno"],
        "address": "Cima Bosque Mesófilo, Lote 4",
    },
    {
        "slug": "cabana-ceiba-alta",
        "name": "Cabaña Ceiba Alta",
        "type": "Cabaña",
        "price": 980,
        "capacity": "4 pers",
        "rating": 4.6,
        "reviews": 92,
        "amenities": ["Cocineta", "Terraza", "Baño privado"],
        "address": "Predio La Ceiba, Sendero Sur",
    },
    {
        "slug": "refugio-luciernaga",
        "name": "Refugio Luciérnaga",
        "type": "Cabaña",
        "price": 1580,
        "capacity": "6 pers",
        "rating": 4.7,
        "reviews": 78,
        "amenities": ["Chimenea", "Cocina equipada", "Jardín", "Wi-Fi"],
        "address": "Sierra Norte, acceso por Pinos",
    },
    {
        "slug": "camping-del-arroyo",
        "name": "Camping del Arroyo",
        "type": "Camping",
        "price": 540,
        "capacity": "4 pers",
        "rating": 4.3,
        "reviews": 64,
        "amenities": ["Asadores", "Baños comunes"],
        "address": "Ribera del Arroyo, Lote 2",
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


def map_view(request):
    return render(request, "core/map.html", _context("map", hide_footer=True))


def park_list(request):
    return render(request, "core/park_list.html", _context("park_list"))


def park_detail(request, slug):
    park = next((item for item in PARKS if item["slug"] == slug), PARKS[2])
    return render(request, "core/park_detail.html", _context("park_list", selected_park=park))


def login_view(request):
    return render(request, "core/auth/login.html", _context("login"))


def register(request):
    return render(request, "core/auth/register.html", _context("register"))


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
