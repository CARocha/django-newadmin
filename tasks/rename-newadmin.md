# Identidad y repositorio — django-newadmin

Solicitud del usuario: nueva identidad para el tema y traslado al repositorio
CARocha/django-newadmin en la carpeta personal del mismo nombre.

- Distribución: django-newadmin; módulo/aplicación: newadmin; marca: NewAdmin.
- Configuración pública: NEWADMIN. Bloques, tags, rutas de recursos, clases y
  variables CSS usan el prefijo newadmin. No se mantienen aliases anteriores:
  todavía no hay una distribución pública que requiera compatibilidad.
- Versión inicial: 0.1.0a1. Licencia BSD de 3 cláusulas y diseño conservados.
- El historial Git se importa íntegro en el nuevo clon; no se reescriben commits.
- Datos de demo conservados localmente, siempre ignorados por Git.
- Validar matriz, recursos, Sphinx, wheel/sdist e instalación limpia; revisar la
  ausencia de referencias anteriores en los archivos actuales y subir main al
  origin nuevo, sin publicar todavía en TestPyPI/PyPI.

## Evidencia

- La prueba de identidad falló antes del cambio por ausencia del módulo nuevo.
- La configuración, recursos y plantillas se verifican con el nombre nuevo.

- Matriz final: 101 pruebas pasan en cada combinación Django 6.0.9/6.1.2 ×
  Python 3.13/3.14; cuatro pruebas JavaScript, Ruff y checks pasan.
- Sphinx estricto y Twine validan la documentación y las distribuciones nuevas.
  Wheel instalado fuera del checkout; login/formularios/manifiesto verificados.
- Revisión independiente: comparación normalizada de todos los archivos;
  continuidad funcional y licencias conservadas. Sin hallazgos funcionales.
