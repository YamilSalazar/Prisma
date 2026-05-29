from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Usuario


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