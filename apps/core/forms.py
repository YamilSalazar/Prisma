from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm


Usuario = get_user_model()


class RegisterForm(UserCreationForm):

    first_name = forms.CharField(
        label="Nombre",
        max_length=150
    )

    last_name = forms.CharField(
        label="Apellidos",
        max_length=150
    )

    email = forms.EmailField(
        label="Correo electrónico"
    )

    telefono = forms.CharField(
        label="Teléfono",
        max_length=20,
        required=False
    )

    class Meta:
        model = Usuario

        fields = [
            "first_name",
            "last_name",
            "email",
            "telefono",
            "idioma",
            "password1",
            "password2",
        ]

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if Usuario.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "Ya existe una cuenta registrada con este correo."
            )

        return email