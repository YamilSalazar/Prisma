from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from .utils import amenity_icon


class UsuarioManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("El correo electrónico es obligatorio.")

        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("rol", "administrador")

        if extra_fields.get("is_staff") is not True:
            raise ValueError("El superusuario debe tener is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("El superusuario debe tener is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class Usuario(AbstractUser):
    ROLES = [
        ("cliente", "Cliente"),
        ("administrador", "Administrador"),
    ]

    IDIOMAS = [
        ("es", "Español"),
        ("en", "English"),
    ]

    username = None

    email = models.EmailField(
        "correo electrónico",
        unique=True
    )

    telefono = models.CharField(
        "teléfono",
        max_length=20,
        blank=True
    )

    rol = models.CharField(
        max_length=20,
        choices=ROLES,
        default="cliente"
    )

    idioma = models.CharField(
        max_length=2,
        choices=IDIOMAS,
        default="es"
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UsuarioManager()

    def __str__(self):
        return self.email


# ──────────────────────────────────────────────────────────────────
# Catálogo de parques
# ──────────────────────────────────────────────────────────────────
class Parque(models.Model):
    """Hospedaje oficial del festival.

    Las @property con nombres en inglés (name, type, price, capacity, reviews,
    images, amenities, amenity_items) existen para que las plantillas actuales
    sigan funcionando sin cambios tras migrar de la lista hardcodeada `PARKS`.
    """

    TIPOS = [
        ("Cabaña", "Cabaña"),
        ("Camping", "Camping"),
    ]

    slug = models.SlugField("identificador", unique=True)
    nombre = models.CharField("nombre", max_length=120)
    tipo = models.CharField("tipo", max_length=20, choices=TIPOS, default="Cabaña")
    precio = models.PositiveIntegerField("precio por noche", default=0)

    capacidad_personas = models.PositiveSmallIntegerField("capacidad por hospedaje", default=4)
    capacidad_cabanas = models.PositiveSmallIntegerField("cupo de cabañas", default=0)
    capacidad_camping = models.PositiveSmallIntegerField("cupo de zonas de camping", default=0)

    rating = models.DecimalField("calificación", max_digits=2, decimal_places=1, default=4.5)
    direccion = models.CharField("dirección", max_length=200, blank=True)
    lat = models.FloatField("latitud", default=19.46)
    lng = models.FloatField("longitud", default=-98.55)

    carpeta_imagenes = models.CharField(
        "carpeta de imágenes",
        max_length=80,
        help_text="Nombre de la carpeta en static/core/assets/parks/",
    )

    activo = models.BooleanField("activo", default=True)
    ultima_edicion = models.DateTimeField("última edición", auto_now=True)

    class Meta:
        verbose_name = "parque"
        verbose_name_plural = "parques"
        ordering = ["-rating", "nombre"]

    def __str__(self):
        return self.nombre

    # — Alias para compatibilidad con las plantillas existentes —
    @property
    def name(self):
        return self.nombre

    @property
    def type(self):
        return self.tipo

    @property
    def price(self):
        return self.precio

    @property
    def address(self):
        return self.direccion

    @property
    def capacity(self):
        return f"{self.capacidad_personas} pers"

    @property
    def reviews(self):
        return self.resenas.count()

    @property
    def images(self):
        return [
            f"core/assets/parks/{self.carpeta_imagenes}/imagen{i}.jpg"
            for i in range(1, 6)
        ]

    @property
    def amenities(self):
        return [a.label for a in self.amenidades.all()]

    @property
    def amenity_items(self):
        return [
            {"label": a.label, "icon": amenity_icon(a.label)}
            for a in self.amenidades.all()
        ]

    @property
    def capacidad_total(self):
        return self.capacidad_cabanas + self.capacidad_camping


class Amenidad(models.Model):
    parque = models.ForeignKey(
        Parque, related_name="amenidades", on_delete=models.CASCADE
    )
    label = models.CharField("amenidad", max_length=80)

    class Meta:
        verbose_name = "amenidad"
        verbose_name_plural = "amenidades"
        ordering = ["id"]

    def __str__(self):
        return f"{self.label} ({self.parque.nombre})"

    @property
    def icon(self):
        return amenity_icon(self.label)


# ──────────────────────────────────────────────────────────────────
# Reseñas
# ──────────────────────────────────────────────────────────────────
class Resena(models.Model):
    parque = models.ForeignKey(
        Parque, related_name="resenas", on_delete=models.CASCADE
    )
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="resenas",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
    )
    autor_nombre = models.CharField("autor", max_length=120)
    rating = models.PositiveSmallIntegerField("calificación", default=5)
    comentario = models.TextField("comentario")
    verificada = models.BooleanField("verificada", default=True)
    creada = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "reseña"
        verbose_name_plural = "reseñas"
        ordering = ["-creada"]

    def __str__(self):
        return f"{self.autor_nombre} · {self.parque.nombre} ({self.rating}★)"

    @property
    def iniciales(self):
        partes = [p for p in self.autor_nombre.split() if p]
        return "".join(p[0] for p in partes[:2]).upper() or "?"

    @property
    def estrellas(self):
        """Cadena de 5 estrellas (llenas/vacías) para pintar la calificación."""
        return "★" * self.rating + "☆" * (5 - self.rating)


# ──────────────────────────────────────────────────────────────────
# Disponibilidad por parque y fecha
# ──────────────────────────────────────────────────────────────────
class Disponibilidad(models.Model):
    ESTADOS = [
        ("available", "Disponible"),
        ("low", "Disponibilidad baja"),
        ("full", "Lleno"),
        ("blocked", "Bloqueado (mantenimiento)"),
    ]

    parque = models.ForeignKey(
        Parque, related_name="disponibilidades", on_delete=models.CASCADE
    )
    fecha = models.DateField("fecha")
    estado = models.CharField("estado", max_length=12, choices=ESTADOS, default="available")
    cupo_cabanas = models.PositiveSmallIntegerField("cupo de cabañas", default=0)
    cupo_camping = models.PositiveSmallIntegerField("cupo de zonas de camping", default=0)
    reservadas_cabanas = models.PositiveSmallIntegerField("cabañas reservadas", default=0)
    reservadas_camping = models.PositiveSmallIntegerField("zonas reservadas", default=0)

    class Meta:
        verbose_name = "disponibilidad"
        verbose_name_plural = "disponibilidades"
        unique_together = ("parque", "fecha")
        ordering = ["fecha"]

    def __str__(self):
        return f"{self.parque.nombre} · {self.fecha} · {self.estado}"

    @property
    def disponibles_cabanas(self):
        return max(self.cupo_cabanas - self.reservadas_cabanas, 0)

    @property
    def disponibles_camping(self):
        return max(self.cupo_camping - self.reservadas_camping, 0)

    @property
    def reservable(self):
        return self.estado not in ("full", "blocked")


# ──────────────────────────────────────────────────────────────────
# Reservaciones
# ──────────────────────────────────────────────────────────────────
class Reservacion(models.Model):
    ESTADOS = [
        ("activa", "Activa"),
        ("completada", "Completada"),
        ("cancelada", "Cancelada"),
    ]

    folio = models.CharField("folio", max_length=24, unique=True)
    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="reservaciones",
        on_delete=models.CASCADE,
    )
    parque = models.ForeignKey(
        Parque, related_name="reservaciones", on_delete=models.PROTECT
    )
    tipo_hospedaje = models.CharField("tipo de hospedaje", max_length=20, default="Cabaña")
    fecha_entrada = models.DateField("entrada")
    fecha_salida = models.DateField("salida")
    noches = models.PositiveSmallIntegerField("noches", default=1)
    personas = models.PositiveSmallIntegerField("personas", default=1)

    subtotal = models.PositiveIntegerField("subtotal", default=0)
    servicio = models.PositiveIntegerField("servicio", default=0)
    impuestos = models.PositiveIntegerField("impuestos", default=0)
    total = models.PositiveIntegerField("total", default=0)

    estado = models.CharField("estado", max_length=12, choices=ESTADOS, default="activa")
    metodo_pago_marca = models.CharField("marca de tarjeta", max_length=20, blank=True, default="Visa")
    metodo_pago_last4 = models.CharField("últimos 4 dígitos", max_length=4, blank=True)
    creada = models.DateTimeField("creada", auto_now_add=True)

    class Meta:
        verbose_name = "reservación"
        verbose_name_plural = "reservaciones"
        ordering = ["-creada"]

    def __str__(self):
        return f"{self.folio} · {self.parque.nombre}"


# ──────────────────────────────────────────────────────────────────
# Información de contacto del festival (singleton)
# Alimenta el footer público y la pantalla de contacto del admin.
# ──────────────────────────────────────────────────────────────────
class ContactoFestival(models.Model):
    email = models.EmailField("correo de contacto", default="contacto@festival-luciernagas.mx")
    telefono = models.CharField("teléfono", max_length=40, default="+52 (55) 5512 3456")
    horario = models.CharField("horario", max_length=120, default="Lun – Vie · 09:00 – 18:00 hrs")

    instagram = models.CharField("Instagram", max_length=120, blank=True, default="@Festival_LuciernagasMx")
    web = models.CharField("Sitio web", max_length=120, blank=True, default="festival-luciernagas.mx")
    twitter = models.CharField("Twitter / X", max_length=120, blank=True, default="@fila_oficial")
    youtube = models.CharField("YouTube", max_length=120, blank=True, default="@FestivalLuciernagas")

    mensaje_soporte = models.TextField(
        "mensaje de soporte",
        default=(
            "Si necesitas ayuda con tu reservación o tienes preguntas sobre el "
            "Festival Internacional de las Luciérnagas, escríbenos a "
            "contacto@festival-luciernagas.mx. Te responderemos en un máximo de "
            "24 horas hábiles."
        ),
    )
    fechas_festival = models.CharField("fechas del festival", max_length=80, default="12 Jun — 18 Ago 2026")
    num_parques = models.PositiveSmallIntegerField("número de parques", default=6)

    class Meta:
        verbose_name = "información de contacto"
        verbose_name_plural = "información de contacto"

    def __str__(self):
        return "Contacto del festival"

    @classmethod
    def get_solo(cls):
        """Devuelve el único registro de contacto, creándolo con valores por
        defecto si aún no existe."""
        obj = cls.objects.first()
        if obj is None:
            obj = cls.objects.create()
        return obj