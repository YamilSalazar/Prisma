"""Utilidades compartidas del app core."""

import unicodedata


def amenity_icon(label):
    """Devuelve la clase de icono Phosphor para una amenidad dada.

    Movido desde views.py para que los modelos (Parque.amenity_items) y las
    vistas puedan reutilizar el mismo mapeo sin duplicar lógica.
    """
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
