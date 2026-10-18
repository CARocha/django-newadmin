# Dashboards con Apache ECharts

NewAdmin permite sustituir el contenido de la portada con una clase Python y una
plantilla. El admin sigue gestionando acceso, sesión y permisos nativos. No es
necesario cambiar los registros de ModelAdmin ni crear otro AdminSite.

## Activación

Sin configuración adicional se muestran las aplicaciones autorizadas y la
actividad reciente. Este escritorio no carga la biblioteca de gráficos.

Para activar el ejemplo editorial incluido en el proyecto de demostración:

```python
NEWADMIN = {
    "SITE_HEADER": "NewAdmin",
    "DASHBOARD": "demo.catalog.dashboard.EditorialDashboard",
}
```

La demo requiere sus modelos `Article` y `Category`. Un proyecto consumidor debe
crear su propio proveedor, en lugar de depender de los modelos de la demo.

## Proveedor propio

```python
# news/admin_dashboard.py: ejemplo para un proyecto con news.Article.
from django.db.models import Count

from newadmin.dashboard import EChartsDashboard
from .models import Article


class NewsDashboard(EChartsDashboard):
    template_name = "news/admin/dashboard.html"
    permissions = ("news.view_article",)

    def get_context_data(self, request):
        # En un proyecto con organizaciones, aplicar aquí el filtro por usuario
        # u organización antes de agregar datos. Este ejemplo es de un solo sitio.
        articles = Article.objects.all()
        counts = list(
            articles.values("category__name")
            .annotate(total=Count("pk"))
            .order_by("-total")[:8]
        )
        rows = [[row["category__name"] or "Sin categoría", row["total"]] for row in counts]
        return {
            "categories": {
                "id": "news-categories",
                "title": "Entradas por categoría",
                "description": "Las ocho categorías con más entradas",
                "columns": ["Categoría", "Entradas"],
                "rows": rows,
                "option": {
                    "tooltip": {"trigger": "axis"},
                    "xAxis": {"type": "category", "data": [row[0] for row in rows]},
                    "yAxis": {"type": "value", "minInterval": 1},
                    "series": [{"name": "Entradas", "type": "bar",
                                "data": [row[1] for row in rows]}],
                },
            },
        }
```

```python
# settings.py
NEWADMIN = {"DASHBOARD": "news.admin_dashboard.NewsDashboard"}
```

```django
{# templates/news/admin/dashboard.html #}
{% extends "newadmin/dashboard/layout.html" %}

{% block dashboard_title %}Resumen editorial{% endblock %}

{% block dashboard_primary %}
  {% include "newadmin/dashboard/chart.html" with chart=dashboard_data.categories %}
{% endblock %}
```

El proveedor recibe `request`, se instancia por solicitud y devuelve un mapping.
El contexto devuelto queda bajo `dashboard_data`: no sustituye el contexto de
permisos, marca, sesión ni las aplicaciones del AdminSite. Una importación inválida,
una clase incorrecta o un contexto con tipo incorrecto provoca `ImproperlyConfigured`.

`permissions` exige todos los permisos declarados antes de consultar datos o
evaluar `Media`. Si faltan, se muestra el escritorio genérico autorizado. Se puede
sobrescribir `has_permission(request)` para reglas adicionales. Un permiso de modelo
no aplica por sí mismo filtros de organización ni permisos por objeto: el proveedor
debe hacerlo en sus querysets, también antes de sumar o contar.

La portada personalizada se aplica al índice principal. Los índices de aplicación,
listados y formularios conservan sus propias pantallas y comparten la misma
paleta, cabecera y navegación del tema. La selección de un proveedor solo cambia
el contenido de la portada; no hace falta configurarlo para aplicar el estilo al
resto del administrador. Login y popups usan la misma paleta con un marco compacto.

## Plantilla y componentes

`newadmin/dashboard/layout.html` expone estos bloques:

| Bloque | Uso |
|---|---|
| `dashboard_title` | Título del panel |
| `dashboard_actions` | Acciones con una URL y permisos reales |
| `dashboard_primary` | Columna principal, 8/12 desde 1200 px |
| `dashboard_metrics` | Columna de métricas, 4/12 desde 1200 px |
| `dashboard_tables` | Tabla o contenido de ancho completo |
| `dashboard_secondary` | Accesos, actividad u otro contenido posterior |

Los bloques pueden incluir plantillas propias, tablas HTML y componentes Bootstrap.
La composición se apila en móvil y mantiene los mismos estilos en claro y oscuro.
Para una plantilla completamente distinta, `template_name` puede apuntar a otra
plantilla de contenido. No debe incluir un documento HTML completo ni duplicar el
marco del admin.

El componente `newadmin/dashboard/chart.html` recibe `chart`:

- `id`: identificador HTML válido, único en la página. `chart_id` permite cambiarlo
  al reutilizar un gráfico en otro bloque.
- `title`: título visible y accesible. `description`: explicación opcional.
- `option`: opciones ECharts serializables como JSON, sin funciones JavaScript.
- `columns`: títulos de columna de la alternativa tabular.
- `rows`: lista de filas con los datos que presenta el gráfico.

Las filas son necesarias para la alternativa accesible. Si están vacías, se muestra
un estado vacío. El componente escapa el HTML de las celdas y utiliza `json_script`
para los datos. El adaptador fuerza tooltips de texto, no tooltips HTML.

El componente `newadmin/dashboard/metric.html` recibe `metric` con `label`, `value`,
`share` (porcentaje real), `tone` (`success`, `warning` o valor neutro) y un `chart`
opcional. La demo calcula los porcentajes a partir de cantidades reales. Sus
minigráficos representan entradas creadas en los últimos siete días agrupadas por
su estado actual; no representan el historial de cambios de estado.

## Sitios independientes y recursos

```python
NEWADMIN = {
    "DASHBOARD": "news.admin_dashboard.NewsDashboard",
    "SITES": {"operations": {"DASHBOARD": None}},
}
```

Las claves de `SITES` son los nombres de instancia de AdminSite. `None` conserva
el escritorio genérico para ese sitio. Los proveedores no comparten instancias ni
datos entre solicitudes.

Se puede heredar de `Dashboard` para un panel sin ECharts. `EChartsDashboard`
incluye el runtime local y su adaptador. Una clase `Media` añade CSS o JavaScript
propio, conservando los recursos heredados mediante el mecanismo nativo de Django:

```python
class NewsDashboard(EChartsDashboard):
    # ...
    class Media:
        css = {"all": ["news/dashboard.css"]}
        js = ["news/dashboard.js"]
```

En Django 6.1, el renderizado de Media usa el mecanismo nativo de nonce cuando el
contexto lo proporciona. Una política CSP concreta y las personalizaciones del
consumidor necesitan su propia verificación; no se exige habilitar `unsafe-eval`.

## Comportamiento y límites

- Los gráficos usan SVG y se redimensionan con su contenedor. Respetan el modo
  claro/oscuro/automático y la preferencia de movimiento reducido.
- El cambio de tema conserva la selección de la leyenda y el rango de zoom.
- ECharts aporta descripciones ARIA; la tabla alternativa se conserva sin JavaScript.
  Esto no certifica por sí solo navegación por teclado o conformidad WCAG completa.
- El adaptador inicializa los gráficos presentes al cargar la página. Si un
  proyecto inserta gráficos dinámicamente, debe gestionar ese ciclo de vida con
  su propio JavaScript y la API de ECharts.
- Errores de inicialización se registran en consola y los datos tabulares permanecen
  disponibles. No hay peticiones a CDN ni a servicios de exportación.
- El tema no crea consultas automáticas para modelos arbitrarios. El proveedor
  decide los filtros, agregaciones, límites y reglas de negocio.

## Distribución y desarrollo

ECharts 6.1.0 está fijado en npm. El paquete Python incluye el runtime compilado,
LICENSE, NOTICE y los avisos de d3, zrender y tslib. No hay pagos de licencia para
activar estos gráficos. Se deben conservar esos avisos al redistribuir los recursos.

```sh
npm ci
npm run build:charts
npm run build:css
```

Estos comandos son para desarrollar el tema. Instalar el wheel no requiere Node.
Se distribuye la compilación completa de ECharts para admitir los tipos de gráficos
del consumidor; su tamaño minificado es aproximadamente 1.1 MB y solo se carga
cuando el proveedor declara esos recursos.

Referencias: [opciones de ECharts](https://echarts.apache.org/en/option.html),
[temas](https://echarts.apache.org/handbook/en/concepts/style/),
[licencia](https://github.com/apache/echarts/blob/master/LICENSE).
