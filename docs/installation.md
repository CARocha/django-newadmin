# Instalación

## Requisitos

- Un entorno virtual con Python 3.13 o 3.14.
- Un proyecto con el administrador de Django 6.0 o 6.1 habilitado.
- `django.contrib.staticfiles` y su configuración habitual de archivos estáticos.

## Instalar el paquete

Mientras el candidato no esté publicado, instala el wheel proporcionado por el
mantenedor (ajusta la ruta):

```sh
python -m pip install /ruta/django_newadmin-0.1.0a1-py3-none-any.whl
```

Después de su publicación en PyPI, el comando será:

```sh
python -m pip install 'django-newadmin==0.1.0a1'
```

Fijar la versión selecciona explícitamente esta alfa. El paquete resuelve Django
como dependencia dentro de su rango soportado. Si ya tienes Django, comprueba el
plan de actualización de pip antes de modificar un entorno de producción.

## Activar en un proyecto existente

En `settings.py`, coloca `newadmin` **antes** de `django.contrib.admin`:

```python
INSTALLED_APPS = [
    'newadmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Tus aplicaciones...
]
```

Conserva los procesadores de contexto `request`, `auth` y `messages`, el middleware
habitual del admin y `APP_DIRS=True` (o el loader de aplicaciones equivalente).
El proyecto creado con `startproject` ya incluye esta configuración.

No cambies tus registros de ModelAdmin ni añadas middleware del tema. No hay
migraciones propias. Si creas el proyecto desde cero, aplica las migraciones
**de Django** y crea un administrador:

```sh
python manage.py migrate
python manage.py createsuperuser
python manage.py check
python manage.py runserver
```

En `urls.py` debe estar montado el admin:

```python
from django.contrib import admin
from django.urls import path

urlpatterns = [path('admin/', admin.site.urls)]
```

Abre `/admin/`. El tema aplica su estilo a login, portada, listados, formularios,
widgets y páginas auxiliares. La configuración `NEWADMIN` es opcional:

```python
NEWADMIN = {'SITE_HEADER': 'Mi sitio', 'DEFAULT_MODE': 'auto'}
```

Continúa con [configuración](configuration.md) y [dashboards](dashboard.md).

## Archivos estáticos en producción

Configura `STATIC_URL`, `STATIC_ROOT` y el servicio de estáticos como harías con
Django. Ejemplo de almacenamiento con manifiesto:

```python
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {
        'BACKEND': 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage',
    },
}
```

```sh
python manage.py collectstatic --noinput
```

Sirve ese directorio con tu servidor de estáticos; `runserver` no es el servidor
para producción. No sustituyas el almacenamiento `default` si tu proyecto ya
lo configura para archivos subidos. Conserva también tu backend de staticfiles
si ya usa otra implementación compatible con Django.

El wheel contiene CSS, JavaScript, iconos y ECharts. `collectstatic` debe ejecutarse
tras cada actualización. Las rutas `LOGO`/`CUSTOM_CSS` se resuelven mediante
staticfiles. Con un CDN en otro origen, verifica la carga de los SVG externos y
la política CORS de tu despliegue; la matriz inicial valida recursos del mismo origen.

## Desactivar o actualizar

Para desactivar el tema, retira `newadmin` de `INSTALLED_APPS` y los overrides del
consumidor que dependan de sus plantillas. El admin vuelve al estilo de Django.
Para actualizar, instala la versión deseada, revisa el changelog, repite
`collectstatic` y prueba tus overrides, formularios y dashboards en staging.

## Demo local del repositorio

Desde un checkout del proyecto:

```sh
python -m venv .venv
.venv/bin/python -m pip install -e '.[dev,docs]'
.venv/bin/python demo/manage.py migrate
.venv/bin/python demo/manage.py seed_demo
.venv/bin/python demo/manage.py createsuperuser
.venv/bin/python demo/manage.py runserver
```

La demo usa SQLite y es para desarrollo local. Los consumidores del tema no
necesitan instalar ni copiar `demo`.
