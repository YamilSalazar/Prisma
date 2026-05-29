from django.shortcuts import render, redirect 
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout 

from .forms import RegisterForm 


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

