# FILA Admin — Estructura modular de templates

El panel admin ha sido dividido en módulos independientes siguiendo la convención de Django templates.

## Estructura de archivos

```
admin/
├── admin-prisma.html          ← Shell principal (131 líneas vs. 2402 originales)
├── admin.css                  ← Todos los estilos del panel
├── partials/
│   ├── _sidebar.html          ← Sidebar reutilizable con active_section variable
│   ├── _dev-switcher.html     ← Barra de navegación de prototipo
│   └── _admin-scripts.html    ← JS compartido (showScreen, modales, etc.)
└── screens/
    ├── _panel.html            ← Panel de control (métricas + últimas reservaciones)
    ├── _parques.html          ← Listado de parques
    ├── _agregar.html          ← Formulario: agregar parque
    ├── _editar.html           ← Formulario: editar parque
    ├── _eliminar.html         ← Confirmación de eliminación con modal
    ├── _reservaciones.html    ← Gestión de reservaciones
    ├── _detalle.html          ← Detalle de reservación individual
    ├── _disponibilidad.html   ← Calendario de disponibilidad + modal de edición
    └── _contacto.html         ← Mensajes de contacto
```

## Uso del sidebar

El partial `_sidebar.html` acepta la variable `active_section` para marcar
el enlace activo en cada pantalla:

```django
{% include "core/admin/partials/_sidebar.html" with active_section="panel" %}
{% include "core/admin/partials/_sidebar.html" with active_section="parques" %}
{% include "core/admin/partials/_sidebar.html" with active_section="reservaciones" %}
{% include "core/admin/partials/_sidebar.html" with active_section="disponibilidad" %}
{% include "core/admin/partials/_sidebar.html" with active_section="contacto" %}
```

## Nota: screen-eliminar

Esta pantalla tiene una estructura especial: el modal de confirmación de
eliminación se encuentra fuera del `admin-shell` pero dentro del `screen`.
El archivo `_eliminar.html` cierra el `</div>` del `admin-shell` y contiene
el modal, por lo que en `admin-prisma.html` se gestiona de forma distinta
al resto de pantallas.

## Paleta de colores

Definida como CSS custom properties en `admin.css`:

| Variable      | HEX       | Rol                                    |
|---------------|-----------|----------------------------------------|
| `--night`     | `#0F1A0D` | Fondo principal                        |
| `--deep`      | `#1A3320` | Superficies secundarias                |
| `--gold`      | `#C8975A` | Botones CTA, precio, marca             |
| `--cream`     | `#F0EDE5` | Texto principal sobre fondos oscuros   |
| `--terracota` | `#B8552A` | Botones de búsqueda y acción secundaria|
| `--green`     | `#2F7D49` | Estados de éxito                       |
| `--red`       | `#C6483A` | Errores y eliminación                  |
| `--amber`     | `#B8862A` | Advertencias y disponibilidad limitada |
