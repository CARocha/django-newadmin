# Resolución de problemas

## Se sigue viendo el admin de Django

Comprueba que instalaste el paquete en el mismo entorno que ejecuta Django y que
`newadmin` precede a `django.contrib.admin`. Revisa los overrides en `TEMPLATES['DIRS']`
y las aplicaciones anteriores a `newadmin`: pueden ocultar las plantillas del tema.

```sh
python -m pip show django-newadmin
python manage.py check
python manage.py findstatic newadmin/css/newadmin.css --verbosity 2
```

## Estáticos ausentes, sin estilos o iconos

Ejecuta `collectstatic`, verifica `STATIC_URL` y el servicio de estáticos, y limpia
la caché del navegador. No mezcles plantillas de una versión con CSS de otra.
`ManifestStaticFilesStorage` necesita todos los archivos del paquete en su manifiesto.

## Errores de configuración

Los checks del tema distinguen ajustes inválidos (`newadmin.E001`/`E002`), rutas de
recursos (`E003`), menú (`E004`) y orden de aplicaciones (`E005`). El mensaje indica
qué corregir. `LOGO`/`CUSTOM_CSS` usan rutas de staticfiles, sin URL externa ni `..`.

Si un enlace nombrado no se puede resolver, comprueba su nombre, namespace y el
registro de modelos en ese AdminSite. No se usa otro sitio como fallback. Los
modelos/enlaces ocultos pueden deberse a permisos: no desactives su comprobación.

## El dashboard no aparece o no muestra datos

Comprueba la ruta importable de `DASHBOARD`, la subclase, `template_name` y los
permisos del usuario. Sin permisos se muestra el escritorio genérico. Los datos
se filtran en el proveedor, no en el frontend. Revisa la consola si falla ECharts;
los datos deben seguir disponibles en la tabla alternativa.

## Personalizaciones que cambian el contraste o los controles

Comprueba los tres modos y la navegación con teclado después de añadir CSS o
widgets. Conserva `block.super` en los bloques de recursos. Prueba por separado
las pantallas del admin que sustituyas completamente.

Al reportar un problema incluye versiones de Python/Django/NewAdmin, navegador,
pantalla afectada, pasos y un ejemplo mínimo sin credenciales ni datos personales.
