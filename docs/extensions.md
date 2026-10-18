# Referencia de extensiones

La [guía de configuración](configuration.md) detalla las opciones, los iconos,
los enlaces con permisos, los sitios independientes y los bloques de plantillas.
La [guía de dashboards](dashboard.md) contiene un ejemplo de agregaciones por
categoría, la plantilla, la alternativa tabular y el aislamiento de datos.

## API Python de dashboards

```{eval-rst}
.. autoclass:: newadmin.dashboard.Dashboard
   :members: has_permission, get_context_data

.. autoclass:: newadmin.dashboard.EChartsDashboard
```

`template_name` selecciona una plantilla de contenido. `permissions` contiene
permisos Django exigidos antes de obtener datos. No anula permisos por objeto o
por organización: aplícalos también en tus querysets. `Media` funciona como en
los widgets de Django y conserva los recursos heredados.

## Recursos y widgets de terceros

El tema conserva los scripts nativos, inlines y `django.jQuery`; no añade otra
copia de jQuery. Declara los recursos de tus widgets en su `Media` habitual.

No se instala ningún editor de texto enriquecido. TinyMCE, StreamField u otros
widgets pueden añadirse en el proyecto consumidor, pero sus versiones y estilos
requieren una comprobación independiente. No se anuncian como integraciones
soportadas de esta alfa.

No dependas de funciones Python privadas, detalles internos del DOM o el prefijo
`_`. Los puntos públicos son `NEWADMIN`, los bloques documentados, los proveedores
y los tokens visuales. Durante la alfa pueden cambiar con notas de migración.
