"""Diccionario de traducciones ES/EN (toggle ligero de idioma).

El context processor `idioma` inyecta `t` (el diccionario del idioma activo) en
todas las plantillas. Las plantillas usan `{{ t.clave }}`. Cubre las cadenas
principales de la interfaz (navbar, footer, home, ficha de parque, flujo de
reserva, cuenta). Si una clave no existe en el idioma activo, el motor de
plantillas la deja vacía, por lo que conviene mantener ambos idiomas en sincronía.
"""

LANGS = ("es", "en")

ES = {
    # — Navbar / menú —
    "nav_inicio": "Inicio",
    "nav_mapa": "Mapa",
    "nav_parques": "Parques",
    "nav_reservaciones": "Mis reservaciones",
    "nav_cuenta": "Mi cuenta",
    "nav_login": "Iniciar sesión",
    "nav_register": "Registrarse",
    "nav_menu": "Menú",
    "nav_cerrar": "Cerrar menú",
    "nav_idioma": "Idioma",

    # — Footer —
    "footer_tagline": "El espectáculo natural de bioluminiscencia más grande de México, en los bosques de Nanacamilpa, Tlaxcala.",
    "footer_explore": "Explorar",
    "footer_contact": "Contacto",
    "footer_follow": "Síguenos",
    "footer_legal": "Legal",
    "footer_about": "Acerca del festival",
    "footer_support": "Soporte",
    "footer_privacy": "Privacidad",
    "footer_terms": "Términos y condiciones",
    "footer_rights": "Todos los derechos reservados",
    "footer_dates": "Temporada",
    "footer_schedule": "Horario",
    "footer_phone": "Teléfono",

    # — Home —
    "hero_eyebrow": "Edición 2026 · Sitio oficial",
    "hero_parks_word": "parques",
    "hero_nights": "2 — 5 noches",
    "hero_official": "Oficial",
    "btn_ver_mapa": "Ver mapa",
    "featured_eyebrow": "Hospedajes destacados",
    "featured_title_1": "Tres opciones que",
    "featured_title_2": "se llenan primero",
    "featured_ver_todos": "Ver todos",

    # — Listado de parques —
    "list_filtros": "Filtros",
    "list_tipo": "Tipo de hospedaje",
    "list_todos": "Todos",
    "list_cabana": "Cabaña",
    "list_camping": "Camping",
    "list_capacidad": "Capacidad",
    "list_precio": "Rango de precio",
    "list_buscar": "Buscar por nombre de parque, hospedaje o amenidad...",
    "list_parques_word": "parques",
    "list_disponible": "Disponible esta semana",

    # — Ficha de parque —
    "pd_oficial": "Oficial",
    "pd_resenas_word": "reseñas",
    "pd_servicios": "Servicios y amenidades",
    "pd_horario": "Horario de atención",
    "pd_calificaciones": "Calificaciones",
    "pd_resenas_verificadas": "reseñas verificadas",
    "pd_ver_resenas_1": "Ver las",
    "pd_ver_resenas_2": "reseñas",
    "pd_ocultar_resenas": "Ocultar reseñas",
    "pd_reglamento": "Reglamento",
    "pd_ubicacion": "Ubicación",
    "pd_ver_mapa": "Ver en el mapa",
    "pd_fechas": "Fechas",
    "pd_personas": "Personas",
    "pd_tipo_hospedaje": "Tipo de hospedaje",
    "pd_noche": "/ noche",
    "btn_reservar": "Reservar",
    "pd_no_cobro": "No se cobra hasta confirmar el pago",

    # — Flujo de reserva —
    "btn_continuar": "Continuar",
    "btn_volver": "Volver",
    "btn_ir_pagar": "Ir a pagar",
    "btn_modificar": "Modificar datos",
    "step_datos": "Datos",
    "step_resumen": "Resumen",
    "step_pago": "Pago",
    "step_confirmacion": "Confirmación",

    # — Cuenta —
    "acc_mi_cuenta": "Mi cuenta",
    "acc_cerrar_sesion": "Cerrar sesión",

    # — Genéricos —
    "g_disponible": "Disponible",
    "g_total": "Total",
}

EN = {
    # — Navbar / menu —
    "nav_inicio": "Home",
    "nav_mapa": "Map",
    "nav_parques": "Parks",
    "nav_reservaciones": "My bookings",
    "nav_cuenta": "My account",
    "nav_login": "Sign in",
    "nav_register": "Sign up",
    "nav_menu": "Menu",
    "nav_cerrar": "Close menu",
    "nav_idioma": "Language",

    # — Footer —
    "footer_tagline": "Mexico's largest natural bioluminescence show, in the forests of Nanacamilpa, Tlaxcala.",
    "footer_explore": "Explore",
    "footer_contact": "Contact",
    "footer_follow": "Follow us",
    "footer_legal": "Legal",
    "footer_about": "About the festival",
    "footer_support": "Support",
    "footer_privacy": "Privacy",
    "footer_terms": "Terms & conditions",
    "footer_rights": "All rights reserved",
    "footer_dates": "Season",
    "footer_schedule": "Hours",
    "footer_phone": "Phone",

    # — Home —
    "hero_eyebrow": "2026 Edition · Official site",
    "hero_parks_word": "parks",
    "hero_nights": "2 — 5 nights",
    "hero_official": "Official",
    "btn_ver_mapa": "View map",
    "featured_eyebrow": "Featured stays",
    "featured_title_1": "Three options that",
    "featured_title_2": "fill up first",
    "featured_ver_todos": "See all",

    # — Parks list —
    "list_filtros": "Filters",
    "list_tipo": "Lodging type",
    "list_todos": "All",
    "list_cabana": "Cabin",
    "list_camping": "Camping",
    "list_capacidad": "Capacity",
    "list_precio": "Price range",
    "list_buscar": "Search by park name, lodging or amenity...",
    "list_parques_word": "parks",
    "list_disponible": "Available this week",

    # — Park detail —
    "pd_oficial": "Official",
    "pd_resenas_word": "reviews",
    "pd_servicios": "Services & amenities",
    "pd_horario": "Opening hours",
    "pd_calificaciones": "Ratings",
    "pd_resenas_verificadas": "verified reviews",
    "pd_ver_resenas_1": "See the",
    "pd_ver_resenas_2": "reviews",
    "pd_ocultar_resenas": "Hide reviews",
    "pd_reglamento": "Rules",
    "pd_ubicacion": "Location",
    "pd_ver_mapa": "View on the map",
    "pd_fechas": "Dates",
    "pd_personas": "Guests",
    "pd_tipo_hospedaje": "Lodging type",
    "pd_noche": "/ night",
    "btn_reservar": "Book now",
    "pd_no_cobro": "You won't be charged until payment is confirmed",

    # — Booking flow —
    "btn_continuar": "Continue",
    "btn_volver": "Back",
    "btn_ir_pagar": "Go to payment",
    "btn_modificar": "Edit details",
    "step_datos": "Details",
    "step_resumen": "Summary",
    "step_pago": "Payment",
    "step_confirmacion": "Confirmation",

    # — Account —
    "acc_mi_cuenta": "My account",
    "acc_cerrar_sesion": "Sign out",

    # — Generic —
    "g_disponible": "Available",
    "g_total": "Total",
}

TRANSLATIONS = {"es": ES, "en": EN}


def get_dict(lang):
    return TRANSLATIONS.get(lang, ES)
