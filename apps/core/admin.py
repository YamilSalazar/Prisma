from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import (
    Amenidad,
    ContactoFestival,
    Disponibilidad,
    Parque,
    Reservacion,
    Resena,
    Usuario,
)


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    model = Usuario

    list_display = (
        "email",
        "first_name",
        "last_name",
        "rol",
        "idioma",
        "telefono",
        "is_active",
        "is_staff",
    )

    list_filter = (
        "rol",
        "idioma",
        "is_active",
        "is_staff",
        "is_superuser",
    )

    search_fields = (
        "email",
        "first_name",
        "last_name",
        "telefono",
    )

    ordering = ("email",)

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Información personal", {"fields": ("first_name", "last_name", "telefono", "idioma", "rol")}),
        ("Permisos", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Fechas importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "email",
                "first_name",
                "last_name",
                "telefono",
                "idioma",
                "rol",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )


class AmenidadInline(admin.TabularInline):
    model = Amenidad
    extra = 1


@admin.register(Parque)
class ParqueAdmin(admin.ModelAdmin):
    list_display = ("nombre", "tipo", "precio", "capacidad_personas", "rating", "activo")
    list_filter = ("tipo", "activo")
    search_fields = ("nombre", "slug", "direccion")
    prepopulated_fields = {"slug": ("nombre",)}
    inlines = [AmenidadInline]


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = ("autor_nombre", "parque", "rating", "verificada", "creada")
    list_filter = ("rating", "verificada", "parque")
    search_fields = ("autor_nombre", "comentario")


@admin.register(Disponibilidad)
class DisponibilidadAdmin(admin.ModelAdmin):
    list_display = ("parque", "fecha", "estado", "cupo_cabanas", "cupo_camping")
    list_filter = ("estado", "parque")
    date_hierarchy = "fecha"


@admin.register(Reservacion)
class ReservacionAdmin(admin.ModelAdmin):
    list_display = ("folio", "usuario", "parque", "fecha_entrada", "estado", "total")
    list_filter = ("estado", "parque")
    search_fields = ("folio", "usuario__email")


@admin.register(ContactoFestival)
class ContactoFestivalAdmin(admin.ModelAdmin):
    list_display = ("email", "telefono", "fechas_festival")