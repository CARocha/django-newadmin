# Especificación de django-newadmin

Fecha: 2026-10-16. Estado: propuesta concreta derivada del plan aprobado.
Alcance de esta entrega: T01; documento de contrato, todavía sin implementación.
Plan aprobado: [tasks/plan.md](tasks/plan.md). Diseño: [DESIGN.md](DESIGN.md).

## 1. Objetivo y usuarios

Tema para equipos que usan el admin de Django y quieren una navegación familiar
clara y adaptable, formularios cómodos y una apariencia consistente en claro y
oscuro. Instalarlo no debe exigir cambiar modelos, registros de ModelAdmin ni
el AdminSite existente. El éxito se mide por recorridos administrativos completos,
no solamente por capturas del inicio.

El paquete es una única capacidad: presentación y navegación del admin. Django
sigue siendo responsable de autenticación, permisos, formularios, acciones,
validaciones y persistencia. Los editores enriquecidos son integraciones futuras
independientes y quedan fuera de esta especificación.

## 2. Plataforma y distribución

- Distribución: `django-newadmin`; módulo y etiqueta de aplicación: `newadmin`.
- Python: 3.13 y 3.14; Django: últimas revisiones de las series 6.0 y 6.1.
- Primer rango de dependencia previsto: `Django>=6.0,<6.2` y Python `>=3.13`.
  Ese rango expresa las series de Django a verificar; no promete soporte para
  futuras versiones de Python. Los clasificadores anunciarán solo la matriz probada.
- Bootstrap 5.3: importar únicamente las partes necesarias y fijar la revisión
  exacta en el archivo de bloqueo del frontend al implementar.
- JavaScript progresivo sin framework adicional y sin otra copia de jQuery.
- Construcción Python con hatchling; pruebas con pytest y pytest-django;
  automatización de navegador con Playwright y comprobaciones de accesibilidad.
- Dependencia Python de ejecución: Django. Herramientas de desarrollo separadas.
- Wheel y sdist incluyen plantillas y recursos locales compilados. La construcción
  Python desde sdist tampoco exige Node: los recursos ya deben estar incluidos.
- El consumidor usa staticfiles y collectstatic habituales. Sin CDN, fuentes
  remotas, middleware, tablas ni migraciones adicionales del tema.
- Retirar `newadmin` de INSTALLED_APPS devuelve el admin nativo, salvo los overrides
  que el propio consumidor haya añadido a su proyecto.

## 3. Instalación y configuración pública

El proyecto consumidor ya debe tener el admin de Django funcionando con su
configuración estándar de plantillas, context processors y staticfiles.

```python
INSTALLED_APPS = [
    "newadmin",
    "django.contrib.admin",
    # Resto de aplicaciones del proyecto.
]
```

La configuración es opcional. Ausencia de `NEWADMIN` equivale a este contrato:

```python
NEWADMIN = {
    "SITE_TITLE": None,
    "SITE_HEADER": None,
    "LOGO": None,
    "DEFAULT_MODE": "auto",
    "PALETTE": "sapphire",
    "MENU": {"ORDER": [], "ICONS": {}, "LINKS": []},
    "CUSTOM_CSS": [],
    "DASHBOARD": None,
    "SITES": {},
}
```

| Opción | Tipo y semántica |
|---|---|
| SITE_TITLE | Texto o None; None conserva el título del AdminSite actual |
| SITE_HEADER | Texto o None; None conserva la cabecera del AdminSite actual |
| LOGO | Ruta relativa de staticfiles o None; la marca textual sigue siendo accesible |
| DEFAULT_MODE | Uno de light, dark, auto; solo se usa si no hay preferencia válida guardada |
| PALETTE | sapphire en la primera versión; cada futura paleta requiere ambos modos |
| MENU.ORDER | Lista única de app_labels; ordena sin ocultar las aplicaciones no enumeradas |
| MENU.ICONS | Mapa app_label o app_label.model_name a un identificador del catálogo de iconos |
| MENU.LINKS | Enlaces adicionales, en el orden indicado, filtrados por permisos |
| CUSTOM_CSS | Lista ordenada de rutas relativas de staticfiles; se carga después del tema |
| DASHBOARD | Ruta importable a una clase Dashboard o None para el escritorio genérico |
| SITES | Mapa de nombres de instancia AdminSite a overrides parciales |

LOGO y CUSTOM_CSS admiten nombres como `branding/admin.css`; rechazan rutas
absolutas, esquemas URL, segmentos `..`, barras inversas, consultas y fragmentos.
Se resuelven con staticfiles, incluyendo almacenamiento con manifiesto.
No se admiten HTML, SVG ni CSS en línea como valores de configuración.

SITES puede sobrescribir las otras opciones, excepto SITES. Se combinan los
mappings de forma recursiva; las listas se reemplazan completas y None conserva
su significado. La resolución nunca modifica la configuración global ni comparte
listas mutables entre solicitudes. Los nombres son los de AdminSite(name=...),
no las rutas URL. Un sitio sin override usa los valores globales.

Ejemplo de personalización:

```python
NEWADMIN = {
    "SITE_HEADER": "Administración editorial",
    "LOGO": "branding/logo.svg",
    "MENU": {
        "ORDER": ["blog", "auth"],
        "ICONS": {"blog": "file-text", "auth": "users"},
        "LINKS": [{
            "LABEL": "Informes",
            "URL_NAME": "reports:index",
            "ICON": "chart",
            "PERMISSIONS": ["reports.view_report"],
        }],
    },
    "SITES": {"operations": {"SITE_HEADER": "Operaciones"}},
}
```

Un enlace exige LABEL y URL_NAME; ICON es opcional y PERMISSIONS vale [] por
omisión. Se exige que el usuario tenga todos los permisos enumerados. El texto
admite traducción lazy. URL_NAME se resuelve en servidor, con el sitio actual
cuando usa el namespace de aplicación admin. La primera versión admite rutas
sin argumentos y enlaces internos; no acepta URLs arbitrarias ni callbacks de
configuración. Una ruta declarada que no se puede resolver produce un error de
configuración identificable, sin recurrir a un enlace incorrecto.

Catálogo inicial de iconos: grid, file-text, users, settings, folder, image,
calendar, chart, tag, database, globe y link. Son identificadores propios que
mapean a SVG locales. El icono específico de modelo prevalece sobre el de aplicación;
sin ambos, el modelo usa file-text. Una aplicación sin configuración usa folder.
Los iconos decorativos no duplican el nombre accesible de los enlaces.

## 4. Validación y errores

Django system checks valida la configuración al ejecutar check:

- newadmin.E001: NEWADMIN o SITES no es un mapping válido.
- newadmin.E002: opción desconocida, tipo inválido, modo o paleta no admitidos.
- newadmin.E003: ruta de recurso no admitida.
- newadmin.E004: menú inválido, identificador de icono desconocido o app duplicada en ORDER.
- newadmin.E005: newadmin está después de django.contrib.admin en INSTALLED_APPS.

El mensaje incluye la ruta de la opción y la corrección esperada, sin volcar
el objeto de configuración completo. Si se omiten los checks, una configuración
inválida falla con ImproperlyConfigured al resolverse; no se ignoran opciones.
Cambiar ajustes con override_settings se refleja sin reiniciar cachés privadas.
Los app_labels en ORDER e ICONS que no estén registrados en un sitio se ignoran:
es válido compartir ajustes globales entre sitios con modelos diferentes.

## 5. Navegación y comportamiento nativo

- Dos niveles automáticos: aplicación y modelo. Las agrupaciones son las propias
  aplicaciones de Django; no se incorpora un constructor arbitrario de menús.
- Construir sobre la lista y permisos del AdminSite actual, incluyendo el acceso
  de solo vista. Conservar los enlaces de alta cuando el usuario solo puede añadir.
- Apps enumeradas en ORDER primero; las demás conservan su orden relativo nativo.
- La selección actual utiliza identidad de app/modelo y resolución de URL; no
  supone que las claves primarias sean números ni compara prefijos ambiguos.
- Sin modelos autorizados se muestra un estado vacío, sin enlaces rotos.
- Menú plegable con etiqueta accesible y estado expandido visible al teclado.
- Enlaces personalizados no sustituyen la protección de sus vistas. El tema no
  cambia permisos ni añade un sistema de autenticación propio.
- Respetar is_nav_sidebar_enabled: un sitio que deshabilita el lateral conserva esa decisión.
- En popups, conservar el comportamiento nativo y ocultar navegación general.
- Las funcionalidades nativas siguen usando sus scripts, atributos, IDs y Media;
  incluir los recursos una sola vez y conservar su orden de carga.

## 6. Apariencia y varios sitios

La preferencia light/dark/auto es global por origen y navegador, usando la clave
nativa `theme` de localStorage. Marca, paleta y menú se resuelven por AdminSite;
el estado de plegado de navegación se guarda por nombre de sitio y prefijo de URL.
No se almacena la preferencia en el modelo User ni se promete sincronización entre dispositivos.

Un controlador externo sustituye la carga de theme.js en el bloque adecuado,
conservando los valores nativos de data-theme y la semántica del selector accesible.
No se ejecutan dos controladores de clic. data-bs-theme contiene el modo resuelto
light/dark y se actualiza cuando cambia el sistema en modo auto. Una preferencia
explícita ignora el cambio del sistema; eventos storage sincronizan las pestañas.

Si localStorage falla, el control funciona en memoria para esa página. Un valor
guardado inválido usa DEFAULT_MODE. Sin JavaScript, las variables CSS siguen la
preferencia del sistema y la navegación permanece accesible; CRUD continúa
funcionando en los casos que Django admite sin JavaScript. La aplicación de la
apariencia ocurre antes de pintar el contenido para evitar un destello de otro modo.

Recursos externos al tema y nonces CSP de Django se conservan. El tema no exige
habilitar unsafe-inline ni unsafe-eval; las reglas CSP completas del proyecto
consumidor y sus widgets siguen siendo responsabilidad de ese proyecto.

## 7. Plantillas y extensión

- Extender plantillas por bloques y preservar block.super donde corresponda.
- Emplear templates/newadmin para componentes propios y prefijo newadmin- en clases
  nuevas; conservar clases nativas en elementos utilizados por Django.
- Bloques públicos propios: newadmin_branding, newadmin_sidebar_extra y
  newadmin_footer. Documentar contexto y ubicación al implementarlos.
- Conservar bloques nativos de estilos, cabecera y contenido, y el renderizado de Media.
- CUSTOM_CSS y variables --newadmin-* son la API visual. Clases internas y funciones
  Python no documentadas no constituyen una API pública del paquete.
- No exigir un ModelAdmin especial, un AdminSite propio, monkey patches ni
  sustituciones globales de widgets para activar el tema.
- Overrides completos del consumidor pueden necesitar adaptación visual; las
  integraciones de terceros solo se anuncian cuando tienen pruebas propias.

### Dashboard con datos propios (ampliación aprobada el 2026-10-17)

`Dashboard` y `EChartsDashboard` son la API Python documentada para la portada.
El proveedor recibe request, verifica permisos antes de consultar datos, retorna
un mapping bajo dashboard_data y declara su plantilla y Media. Se resuelve por
AdminSite y se instancia una vez por solicitud. No cambia los índices de aplicación
ni exige reemplazar AdminSite. La configuración por omisión sigue siendo None.

Apache ECharts 6.1.0 sustituye a la integración Highcharts propuesta inicialmente.
Sus recursos, licencia y avisos se distribuyen localmente. Se conserva una tabla
alternativa sin JavaScript y no se añade una dependencia Python de gráficos.
Contrato y ejemplos: [docs/dashboard.md](docs/dashboard.md).

## 8. Estructura, estilo y comandos previstos

```text
src/newadmin/         Aplicación distribuible y sus plantillas/staticfiles
assets/             Sass y JavaScript fuente; build reproducible
tests/              Pruebas Python y de navegador
demo/               Proyecto de demostración y datos locales reproducibles
docs/               Instalación, configuración, extensión y soporte
tasks/              Plan y seguimiento
```

Python con anotaciones en las interfaces internas, snake_case, ruff y límites
pequeños por responsabilidad. Plantillas traducibles con gettext; configuración
y contenido escapados según su contexto. JavaScript usa módulos fuente pequeños,
eventos nativos y salida compatible con los navegadores objetivo. Comentarios y
nombres de código en inglés; estos documentos iniciales están en español.

Los siguientes comandos son el contrato de herramientas a crear, no resultados
ya obtenidos. Se ejecutarán desde la raíz una vez implementada su configuración:

```sh
python3.13 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]' build
npm ci
npm run build
.venv/bin/python -m pytest tests --ignore=tests/browser -q
.venv/bin/python -m playwright install chromium
.venv/bin/python -m pytest tests/browser -q
.venv/bin/python -m ruff check .
.venv/bin/python -m ruff format --check .
.venv/bin/python -m build
.venv/bin/python demo/manage.py check
.venv/bin/python demo/manage.py migrate
.venv/bin/python demo/manage.py runserver 127.0.0.1:8000
```

La instalación del wheel y collectstatic se probarán en otro entorno con un
STATIC_ROOT temporal y ManifestStaticFilesStorage, sin depender de fuentes del checkout.

## 9. Verificación y aceptación de la versión estable

- AC01: instalar solo wheel + Django en un proyecto limpio activa el tema al
  añadir newadmin antes del admin, sin cambiar registros ni crear tablas del tema.
- AC02: matriz completa 6.0/6.1 × 3.13/3.14 en verde; soporte futuro separado de main.
- AC03: login, logout POST/CSRF, inicio, aplicaciones e historial funcionan.
- AC04: búsqueda, filtros, facetas, paginación, acciones y list_editable conservan datos y permisos.
- AC05: altas, cambios, errores, readonly, fieldsets e inlines funcionan en ambas series.
- AC06: relaciones, popups, fechas, horas, archivos y Media funcionan, también en nuevos inlines.
- AC07: los tres modos funcionan con cambio de sistema, pestañas y almacenamiento no disponible.
- AC08: dos AdminSite con namespaces y permisos distintos no mezclan enlaces ni marca.
- AC09: teclado, foco, contraste, zoom y RTL verificados; 320, 768, 1024 y 1440 px.
- AC10: wheel/sdist completos, collectstatic con manifiesto correcto y sin solicitudes remotas obligatorias.
- AC11: documentación pública con Sphinx que reproduce instalación, configuración
  y extensiones; limitaciones declaradas y compilación sin advertencias verificada en CI.

Pruebas de lógica con pytest-django; recorridos en navegador con Playwright;
regresión visual para pantallas principales; revisión manual de teclado, RTL y
zoom. El tema no añade consultas de recuento por modelo para decorar el menú.
No se fija un porcentaje de cobertura arbitrario: los contratos y escenarios de
aceptación deben tener pruebas que fallen ante una regresión real.

## 10. Límites de trabajo

Siempre: preservar contratos nativos, verificar cambios, actualizar documentación
cuando cambia configuración y registrar avance real en tasks/todo.md.

Requieren una nueva decisión del usuario: ampliar el núcleo con modelos o un CMS,
cambiar el framework CSS acordado y publicar paquetes, releases o desplegar una demo pública.
Los ajustes rutinarios dentro del alcance aprobado se resuelven y documentan.

Nunca: afirmar soporte no verificado, quitar pruebas para obtener verde, incorporar
secretos o datos personales de muestra, o forzar cambios sobre historia remota.

## 11. Decisiones pendientes de publicación

La licencia del paquete se elegirá antes de publicar. No condiciona el prototipo
local; conservar los avisos de licencia de cualquier recurso distribuido.
Los editores TinyMCE/Quill y StreamField necesitan decisiones y pruebas aparte.
Ninguna de esas decisiones bloquea el núcleo especificado aquí.

## Referencias

- [Admin y personalización](https://docs.djangoproject.com/en/6.0/ref/contrib/admin/).
- [Cambios de Django 6.1](https://docs.djangoproject.com/en/6.1/releases/6.1/).
- [Bootstrap selectivo](https://getbootstrap.com/docs/5.3/customize/optimize/).
- [Modos de Bootstrap](https://getbootstrap.com/docs/5.3/customize/color-modes/).
