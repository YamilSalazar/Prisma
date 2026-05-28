from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models


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