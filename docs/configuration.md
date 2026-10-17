# Configuración, navegación y extensión

El tema funciona al colocar `adminwp` antes de `django.contrib.admin` en
`INSTALLED_APPS`. No exige un `ModelAdmin` ni un `AdminSite` especial.

```python
ADMINWP = {
    "SITE_TITLE": "Mi estudio",
    "SITE_HEADER": "Administración editorial",
    "LOGO": "branding/logo.svg",  # Opcional, ruta de staticfiles.
    "DEFAULT_MODE": "auto",       # light, dark o auto.
    "MENU": {
        "ORDER": ["catalog", "auth"],
        "ICONS": {
            "catalog": "folder",
            "catalog.article": "file-text",
            "catalog.category": "tag",
            "auth.user": "users",
        },
        "LINKS": [{
            "LABEL": "Informes",  # También admite gettext_lazy().
            "URL_NAME": "reports:index",
            "ICON": "chart",
            "PERMISSIONS": ["reports.view_report"],
        }],
    },
    "CUSTOM_CSS": ["branding/admin.css"],
}
```

Los nombres `catalog`, `article`, `category` y `reports:index` son ejemplos: deben
corresponder a las aplicaciones, modelos y rutas de tu proyecto. Las opciones
se validan al ejecutar `python manage.py check` y al resolver el tema.

## Orden, iconos y enlaces

`ORDER` usa `app_label`, sin duplicados. Las aplicaciones omitidas mantienen su
orden nativo después de las enumeradas. Nunca concede permisos ni añade modelos
que Django no haya autorizado para ese usuario y sitio.

`ICONS` acepta claves `app_label` y `app_label.model_name` en minúsculas. El icono
específico del modelo prevalece sobre el de la aplicación; sin configuración se
usan `file-text` para modelos y `folder` para aplicaciones. Se incluyen estos
identificadores estables:

`grid`, `file-text`, `users`, `settings`, `folder`, `image`, `calendar`, `chart`,
`tag`, `database`, `globe`, `link`.

Los SVG son decorativos y locales: las etiquetas siguen dando nombre a cada
entrada. El paquete incluye un subconjunto de Bootstrap Icons 1.13.1 y su
[licencia MIT](https://github.com/twbs/icons/blob/v1.13.1/LICENSE), sin fuentes ni CDN.
La plantilla de lista de aplicaciones conserva la licencia BSD de Django en
`adminwp/vendor/django/LICENSE`. El desarrollador del tema puede reconstruir el sprite con `npm run build:icons`.
Instalar el wheel no requiere npm ni Node.

Cada enlace exige `LABEL` y `URL_NAME`; `ICON` vale `link` y `PERMISSIONS` vale `[]`
por omisión. Solo se muestra cuando el usuario tiene **todos** los permisos
indicados. Los permisos se comprueban antes de resolver su URL.

`URL_NAME` debe ser una ruta interna nombrada y sin argumentos. No admite URLs
arbitrarias, HTML, callbacks ni JavaScript. `admin:nombre_de_vista` usa la instancia
actual de AdminSite, por ejemplo `admin:catalog_article_changelist`. Una ruta
inexistente o no registrada en ese sitio provoca `ImproperlyConfigured` con la
posición del enlace; no se sustituye silenciosamente por otro sitio. Una ruta con
namespace explícito del proyecto conserva ese destino.

El tema oculta accesos, pero la vista de destino debe aplicar sus propios permisos
(por ejemplo, con `admin_site.admin_view()` y una comprobación del permiso de
negocio). El tema no protege una vista pública por añadirla al menú.

El filtro nativo sigue buscando los nombres de los modelos; los iconos y los
enlaces adicionales no alteran sus resultados. La selección del enlace adicional
se marca cuando su URL coincide exactamente con la pantalla actual.

## Varios AdminSite

Las claves de `SITES` son los nombres de instancia de `AdminSite(name=...)`,
independientemente del prefijo donde se montan sus URLs:

```python
# urls.py: un segundo sitio con registros propios.
from django.contrib.admin import AdminSite
from django.urls import path
from news.models import Article

operations = AdminSite(name="operations")
operations.register(Article)
urlpatterns = [path("operations/", operations.urls)]

# settings.py: hereda opciones globales y sustituye solo lo indicado.
ADMINWP = {
    "SITE_HEADER": "Administración",
    "SITES": {
        "operations": {
            "SITE_HEADER": "Operaciones",
            "CUSTOM_CSS": ["branding/operations.css"],
            "MENU": {"ORDER": ["news"], "LINKS": []},
        },
    },
}
```

Los mappings se combinan recursivamente; las listas se reemplazan completas.
`None` conserva su significado, por ejemplo `SITE_HEADER=None` usa la cabecera del
AdminSite y `DASHBOARD=None` conserva el escritorio genérico. Un sitio no configurado
hereda los valores globales. Cada solicitud recibe opciones independientes y
Django conserva los permisos y registros de modelos del sitio actual.

La preferencia light/dark/auto es compartida por origen y navegador, como en Django.
El plegado y el filtro del lateral conservan por ahora el almacenamiento nativo;
la navegación móvil y su adaptación se revisan en T15.

## CSS propio

`LOGO` y `CUSTOM_CSS` son rutas relativas de staticfiles. Se rechazan URLs externas,
rutas absolutas, segmentos `..`, barras inversas, consultas y fragmentos. Funcionan
con `collectstatic` y almacenamiento de manifiesto.

En las plantillas estándar, `CUSTOM_CSS` se carga después de los estilos del tema,
los estilos nativos de la página y el CSS de `ModelAdmin.Media`. Las variables
`--adminwp-*` permiten ajustar la apariencia. Para sustituir colores que se traducen
a variables nativas de Django, define los valores en `:root`/`html`, por ejemplo:

```css
html[data-theme="light"] {
  --adminwp-primary: #184c40;
  --adminwp-primary-hover: #123b31;
}
```

Diseña también la variante oscura y el modo automático si cambias colores que
necesitan variantes. Conserva el contraste de texto, controles y foco.

## Bloques de plantillas

Coloca tus overrides en un directorio de `TEMPLATES['DIRS']` o en una aplicación
antes de `adminwp`. Extiende el mismo nombre y usa `block.super` para conservar el
contenido y los recursos del tema:

```django
{# templates/admin/base_site.html #}
{% extends "admin/base_site.html" %}
{% block adminwp_branding %}{{ block.super }}{% endblock %}
{% block adminwp_footer %}<p>Ayuda del equipo editorial</p>{% endblock %}
```

```django
{# templates/admin/nav_sidebar.html #}
{% extends "admin/nav_sidebar.html" %}
{% block adminwp_sidebar_extra %}
  {{ block.super }}
  {# Contenido adicional del proyecto, con sus comprobaciones de permiso. #}
{% endblock %}
```

`adminwp_branding` está dentro de la marca de cabecera, `adminwp_sidebar_extra`
sigue a las aplicaciones e incluye por defecto `MENU.LINKS`, y `adminwp_footer`
está en el pie del documento. Los bloques reciben el contexto habitual del admin.
El pie tiene contenido vacío por defecto.

Los bloques nativos (`branding`, `extrastyle`, `responsive`, `extrahead`, `content`,
etc.) siguen disponibles. Conserva `block.super` cuando añadas recursos. Los
widgets, inlines y `ModelAdmin.Media` conservan su carga nativa; el tema no exige
sustituirlos ni instala un editor de texto. Overrides completos del consumidor o
integraciones de terceros requieren su propia revisión visual.

Los paneles con datos propios se explican en [dashboard.md](dashboard.md).
