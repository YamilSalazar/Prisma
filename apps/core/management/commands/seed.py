"""Carga datos ficticios coherentes para el Festival de las Luciérnagas.

Uso:
    python manage.py seed

Es idempotente: limpia las tablas de catálogo (parques, reseñas, disponibilidad,
reservaciones, contacto) y las vuelve a poblar. Los usuarios demo se crean con
get_or_create para no duplicarlos ni borrar superusuarios reales.
"""

import datetime as dt
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction

from apps.core.models import (
    Amenidad,
    ContactoFestival,
    Disponibilidad,
    Parque,
    Reservacion,
    Resena,
)

Usuario = get_user_model()

# Temporada del festival 2026
TEMPORADA_INICIO = dt.date(2026, 6, 12)
TEMPORADA_FIN = dt.date(2026, 8, 18)

PARQUES = [
    {
        "slug": "santuario-piedra-canteada",
        "nombre": "Santuario Piedra Canteada",
        "tipo": "Cabaña",
        "precio": 1850,
        "capacidad_personas": 4,
        "capacidad_cabanas": 12,
        "capacidad_camping": 6,
        "rating": 4.9,
        "direccion": "Camino a San Felipe Hidalgo Km 4.5, Nanacamilpa",
        "lat": 19.462312,
        "lng": -98.568421,
        "carpeta_imagenes": "santuario_piedra_canteada",
        "amenidades": ["Chimenea", "Baño privado", "Estacionamiento", "Restaurante"],
    },
    {
        "slug": "canto-del-bosque",
        "nombre": "Canto del Bosque",
        "tipo": "Camping",
        "precio": 750,
        "capacidad_personas": 6,
        "capacidad_cabanas": 4,
        "capacidad_camping": 24,
        "rating": 4.7,
        "direccion": "San Felipe Hidalgo s/n, Nanacamilpa, Tlaxcala",
        "lat": 19.458045,
        "lng": -98.542012,
        "carpeta_imagenes": "canto_del_bosque",
        "amenidades": ["Fogata", "Baños comunes", "Estacionamiento", "Guía certificado"],
    },
    {
        "slug": "santuario-santa-clara",
        "nombre": "Santuario Santa Clara",
        "tipo": "Cabaña",
        "precio": 1420,
        "capacidad_personas": 2,
        "capacidad_cabanas": 10,
        "capacidad_camping": 4,
        "rating": 4.8,
        "direccion": "Camino al Bosque de Santa Clara s/n, Nanacamilpa",
        "lat": 19.459012,
        "lng": -98.535678,
        "carpeta_imagenes": "santa_clara",
        "amenidades": ["Vista panorámica", "Baño privado", "Desayuno"],
    },
    {
        "slug": "bosque-magico",
        "nombre": "Bosque Mágico",
        "tipo": "Cabaña",
        "precio": 1200,
        "capacidad_personas": 4,
        "capacidad_cabanas": 8,
        "capacidad_camping": 6,
        "rating": 4.6,
        "direccion": "Camino Forestal Nanacamilpa, Sendero 4",
        "lat": 19.445089,
        "lng": -98.551045,
        "carpeta_imagenes": "bosque_magico",
        "amenidades": ["Cocineta", "Terraza", "Baño privado"],
    },
    {
        "slug": "santuario-las-minas",
        "nombre": "Santuario Las Minas",
        "tipo": "Cabaña",
        "precio": 1580,
        "capacidad_personas": 6,
        "capacidad_cabanas": 14,
        "capacidad_camping": 8,
        "rating": 4.7,
        "direccion": "Antigua Zona Minera, San Felipe Hidalgo",
        "lat": 19.492567,
        "lng": -98.538012,
        "carpeta_imagenes": "santuario_las_minas",
        "amenidades": ["Chimenea", "Cocina equipada", "Jardín", "Senderismo"],
    },
    {
        "slug": "rancho-el-ciervo",
        "nombre": "Santuario Rancho El Ciervo",
        "tipo": "Camping",
        "precio": 540,
        "capacidad_personas": 4,
        "capacidad_cabanas": 2,
        "capacidad_camping": 22,
        "rating": 4.5,
        "direccion": "Km 8 Carretera Nanacamilpa-Mazapa",
        "lat": 19.470512,
        "lng": -98.555567,
        "carpeta_imagenes": "rancho_el_ciervo",
        "amenidades": ["Asadores", "Baños comunes", "Área recreativa"],
    },
]

RESENAS_POOL = [
    ("María Fernanda C.", 5, "Vista absolutamente increíble. El recorrido nocturno con guía local hizo la diferencia, sí se ven cientos de luciérnagas."),
    ("Roberto J.", 4, "La cabaña súper cómoda y limpia. El acceso es por terracería, ojo si no llevan camioneta alta. Volveremos."),
    ("Claudia P.", 5, "El anfitrión muy atento. La chimenea hizo la noche mucho más cómoda, está fresco aún en junio."),
    ("Diego M.", 5, "Una experiencia mágica en familia. Los niños quedaron encantados con el espectáculo de luces."),
    ("Ana Sofía R.", 4, "Muy buen lugar, limpio y tranquilo. El único detalle es que llegamos tarde y la señalización nocturna podría mejorar."),
    ("Luis Ángel T.", 5, "Sin palabras. El silencio del bosque y las luciérnagas valen totalmente el viaje. Recomendadísimo."),
    ("Gabriela V.", 5, "Atención de primera y el desayuno delicioso. Reservaré de nuevo para la próxima temporada."),
    ("Héctor N.", 4, "Buena relación calidad-precio. Llevar repelente sin DEET como recomiendan, funciona perfecto."),
    ("Paola G.", 5, "El mejor plan para desconectarse. Guía conocedor y respetuoso del hábitat. 10 de 10."),
    ("Fernando Q.", 4, "Hermoso entorno. La fogata por la noche fue lo máximo. Volvería con amigos."),
]

# Clientes ficticios para poblar el panel de administración
CLIENTES = [
    ("maria.h@correo.mx", "María", "Hernández López", "+52 55 1234 5678"),
    ("d.ortega@correo.mx", "Daniel", "Ortega", "+52 55 2233 4455"),
    ("lili.v@correo.mx", "Liliana", "Vargas", "+52 55 3344 5566"),
    ("r.cardenas@correo.mx", "Roberto", "Cárdenas", "+52 55 4455 6677"),
    ("s.reyes@correo.mx", "Sofía", "Reyes", "+52 55 5566 7788"),
    ("a.mendez@correo.mx", "Andrés", "Méndez", "+52 55 6677 8899"),
]


class Command(BaseCommand):
    help = "Carga datos ficticios del festival (parques, reseñas, disponibilidad, reservaciones)."

    @transaction.atomic
    def handle(self, *args, **options):
        rng = random.Random(2026)

        self.stdout.write("Limpiando datos previos…")
        Reservacion.objects.all().delete()
        Disponibilidad.objects.all().delete()
        Resena.objects.all().delete()
        Amenidad.objects.all().delete()
        Parque.objects.all().delete()
        ContactoFestival.objects.all().delete()

        # ── Parques + amenidades ──────────────────────────────────
        parques = {}
        for data in PARQUES:
            amenidades = data.pop("amenidades")
            parque = Parque.objects.create(**data)
            for label in amenidades:
                Amenidad.objects.create(parque=parque, label=label)
            parques[parque.slug] = parque
            data["amenidades"] = amenidades  # restaurar por si se reejecuta
        self.stdout.write(self.style.SUCCESS(f"  · {len(parques)} parques creados"))

        # ── Reseñas (varias por parque, para 'ver todas') ─────────
        total_resenas = 0
        for parque in parques.values():
            n = rng.randint(5, 8)
            elegidas = rng.sample(RESENAS_POOL, n)
            for autor, rating, comentario in elegidas:
                Resena.objects.create(
                    parque=parque,
                    autor_nombre=autor,
                    rating=rating,
                    comentario=comentario,
                    verificada=True,
                )
                total_resenas += 1
        self.stdout.write(self.style.SUCCESS(f"  · {total_resenas} reseñas creadas"))

        # ── Disponibilidad por parque y fecha ─────────────────────
        total_disp = 0
        for parque in parques.values():
            fecha = TEMPORADA_INICIO
            while fecha <= TEMPORADA_FIN:
                es_finde = fecha.weekday() >= 4  # Vie/Sáb/Dom
                cupo_cab = parque.capacidad_cabanas
                cupo_camp = parque.capacidad_camping

                # Bloqueo de mantenimiento ocasional (lunes esporádicos)
                if fecha.weekday() == 0 and rng.random() < 0.18:
                    estado = "blocked"
                    res_cab = res_camp = 0
                else:
                    ocupacion = rng.uniform(0.75, 1.0) if es_finde else rng.uniform(0.25, 0.7)
                    res_cab = round(cupo_cab * ocupacion)
                    res_camp = round(cupo_camp * ocupacion)
                    libres = (cupo_cab - res_cab) + (cupo_camp - res_camp)
                    total = max(cupo_cab + cupo_camp, 1)
                    ratio = libres / total
                    if libres == 0:
                        estado = "full"
                    elif ratio <= 0.2:
                        estado = "low"
                    else:
                        estado = "available"

                Disponibilidad.objects.create(
                    parque=parque,
                    fecha=fecha,
                    estado=estado,
                    cupo_cabanas=cupo_cab,
                    cupo_camping=cupo_camp,
                    reservadas_cabanas=res_cab,
                    reservadas_camping=res_camp,
                )
                total_disp += 1
                fecha += dt.timedelta(days=1)
        self.stdout.write(self.style.SUCCESS(f"  · {total_disp} días de disponibilidad creados"))

        # ── Contacto del festival (singleton) ─────────────────────
        ContactoFestival.objects.create()
        self.stdout.write(self.style.SUCCESS("  · Información de contacto creada"))

        # ── Usuarios demo ─────────────────────────────────────────
        cliente_demo, creado = Usuario.objects.get_or_create(
            email="cliente@fila.mx",
            defaults={
                "first_name": "María Fernanda",
                "last_name": "González Ruiz",
                "telefono": "+52 55 9988 7766",
                "rol": "cliente",
                "is_active": True,
            },
        )
        cliente_demo.set_password("fila2026")
        cliente_demo.save()

        admin_demo, _ = Usuario.objects.get_or_create(
            email="admin@fila.mx",
            defaults={
                "first_name": "Equipo",
                "last_name": "FILA",
                "rol": "administrador",
                "is_staff": True,
                "is_superuser": True,
                "is_active": True,
            },
        )
        admin_demo.set_password("fila2026")
        admin_demo.is_staff = True
        admin_demo.is_superuser = True
        admin_demo.save()

        clientes_extra = []
        for email, nombre, apellidos, tel in CLIENTES:
            u, _ = Usuario.objects.get_or_create(
                email=email,
                defaults={
                    "first_name": nombre,
                    "last_name": apellidos,
                    "telefono": tel,
                    "rol": "cliente",
                    "is_active": True,
                },
            )
            u.set_password("fila2026")
            u.save()
            clientes_extra.append(u)
        self.stdout.write(self.style.SUCCESS(f"  · {2 + len(clientes_extra)} usuarios demo (clave: fila2026)"))

        # ── Reservaciones ─────────────────────────────────────────
        parques_lista = list(parques.values())
        folio_n = 8100
        total_res = 0

        def crea_reservacion(usuario, parque, entrada, noches, personas, estado):
            nonlocal folio_n, total_res
            folio_n += 1
            salida = entrada + dt.timedelta(days=noches)
            subtotal = parque.precio * noches
            servicio = round(subtotal * 0.05)
            impuestos = round((subtotal + servicio) * 0.16)
            Reservacion.objects.create(
                folio=f"FIL-2026-{folio_n:05d}",
                usuario=usuario,
                parque=parque,
                tipo_hospedaje=parque.tipo,
                fecha_entrada=entrada,
                fecha_salida=salida,
                noches=noches,
                personas=personas,
                subtotal=subtotal,
                servicio=servicio,
                impuestos=impuestos,
                total=subtotal + servicio + impuestos,
                estado=estado,
                metodo_pago_marca="Visa",
                metodo_pago_last4=f"{rng.randint(1000, 9999)}",
            )
            total_res += 1

        # Reservaciones del cliente demo (2 activas + 3 historial)
        crea_reservacion(cliente_demo, parques["santuario-santa-clara"], dt.date(2026, 6, 14), 2, 2, "activa")
        crea_reservacion(cliente_demo, parques["bosque-magico"], dt.date(2026, 7, 23), 2, 4, "activa")
        crea_reservacion(cliente_demo, parques["canto-del-bosque"], dt.date(2025, 8, 8), 1, 6, "completada")
        crea_reservacion(cliente_demo, parques["santuario-santa-clara"], dt.date(2025, 7, 17), 2, 2, "cancelada")
        crea_reservacion(cliente_demo, parques["santuario-piedra-canteada"], dt.date(2025, 6, 4), 2, 4, "completada")

        # Reservaciones variadas para poblar el panel admin
        estados = ["activa", "activa", "activa", "completada", "cancelada", "activa"]
        for i, usuario in enumerate(clientes_extra):
            parque = parques_lista[i % len(parques_lista)]
            entrada = dt.date(2026, 7, 12 + (i % 6))
            noches = rng.choice([2, 3])
            personas = rng.choice([2, 3, 4, 6])
            crea_reservacion(usuario, parque, entrada, noches, personas, estados[i % len(estados)])

        self.stdout.write(self.style.SUCCESS(f"  · {total_res} reservaciones creadas"))

        self.stdout.write(self.style.SUCCESS("\n✓ Datos ficticios cargados correctamente."))
        self.stdout.write("  Cliente demo:  cliente@fila.mx / fila2026")
        self.stdout.write("  Admin demo:    admin@fila.mx / fila2026")
