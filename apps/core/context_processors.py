"""Context processors globales del app core.

Inyectan en TODAS las plantillas:
  - LANG: código de idioma activo ('es' | 'en')
  - t: diccionario de traducciones del idioma activo
  - festival_contacto: datos de contacto del festival (para el footer)
"""

from .models import ContactoFestival
from .translations import LANGS, get_dict


def idioma_actual(request):
    """Determina el idioma activo: sesión → usuario → 'es' por defecto."""
    lang = request.session.get("idioma")
    if lang not in LANGS:
        user = getattr(request, "user", None)
        if user is not None and user.is_authenticated and user.idioma in LANGS:
            lang = user.idioma
        else:
            lang = "es"
    return lang


def i18n(request):
    lang = idioma_actual(request)
    return {"LANG": lang, "t": get_dict(lang)}


def festival(request):
    """Datos de contacto del festival para el footer y plantillas públicas."""
    try:
        contacto = ContactoFestival.get_solo()
    except Exception:
        # Durante migraciones la tabla puede no existir todavía.
        contacto = None
    return {"festival_contacto": contacto}
