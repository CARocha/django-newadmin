# Plan inicial de django-adminwp

Fecha: 2026-10-16.
Estado: plan aprobado por el usuario; T01–T13.5 implementadas. T14 es la siguiente tarea.
Tareas y criterios de aceptación: [todo.md](todo.md).

## Objetivo

Crear un tema instalable para el administrador de Django, inspirado en la
navegación de WordPress y en django-wpadmin. Debe ofrecer una presentación
cuidada, modos claro/oscuro/automático y configuración opcional, preservando
los ModelAdmin y los comportamientos nativos de Django.

## Decisiones de partida

- Distribución Python: `django-adminwp`. Módulo y aplicación Django: `adminwp`.
- Matriz inicial prevista: Django 6.0 y 6.1 con Python 3.13 y 3.14.
  La compatibilidad solo se anunciará después de verificar esas combinaciones.
- Bootstrap 5.3 con compilación selectiva de Sass y JavaScript del tema pequeño.
- Recursos compilados incluidos en wheel y sdist. Los consumidores no necesitan
  Node, Sass, fuentes remotas ni una CDN para la instalación habitual.
- Plantillas renderizadas por Django; extensión por bloques y mínima duplicación.
- Mantener scripts y widgets del admin, incluyendo `django.jQuery` cuando Django
  lo requiera. El tema no añadirá otra copia de jQuery.
- Un único estado de apariencia, compatible con el selector nativo de Django.
- Configuración básica mediante `ADMINWP`; menú automático si no se configura.
- Sin modelos, migraciones ni middleware propios para activar el tema.
- Trabajar en esta conversación, sin delegación automática.

## Alcance de la primera versión estable

- Login, inicio, índice de aplicaciones, barra superior y navegación lateral.
- Listados, búsqueda, filtros, facetas, acciones, paginación y `list_editable`.
- Formularios, fieldsets, errores, campos de solo lectura e inlines.
- Widgets nativos: relaciones, autocompletado, selectores múltiples, fechas,
  horas y archivos; conservar los popups de relaciones.
- Confirmaciones de borrado, historial, cambio de contraseña y cierre de sesión.
- Claro, oscuro y automático; diseño adaptable, teclado y RTL.
- Marca, iconos, orden del menú, CSS adicional y configuración por AdminSite.
- Documentación, proyecto de demostración y pruebas de instalación real.

## Releases posteriores

Editores enriquecidos, StreamField, un constructor visual de dashboards y
conversión de popups a modales quedan fuera de la primera versión.
Ampliación aprobada el 2026-10-17: proveedores de dashboard en Python y gráficos
Apache ECharts locales, con la nueva referencia visual suministrada por el usuario.
Las integraciones de terceros tendrán pruebas y matrices de soporte propias.
El tema debe conservar los recursos `Media` de formularios y widgets desde el
inicio para facilitar esas integraciones.

## Diseño y extensibilidad

La primera tarea produjo [DESIGN.md](../DESIGN.md) y [SPEC.md](../SPEC.md): tokens semánticos de color,
tipografía, espaciado, radios, estados de interacción, configuración pública y
contratos de extensión. La referencia Apple se adaptará a tablas y formularios;
la navegación conservará la familiaridad de WordPress.

Las paletas iniciales tendrán variantes completas para claro y oscuro. Los
colores finales se validarán por contraste, no solamente por apariencia.
Los estilos globales de Bootstrap se incorporarán de forma controlada para
evitar interferencias con widgets, páginas de terceros y reglas de Django.

Los menús utilizarán la información de aplicaciones y permisos del AdminSite
actual. Ocultar enlaces no sustituye las comprobaciones de acceso de las vistas.
La configuración por sitio y las preferencias de apariencia se definirán antes
de implementar, incluyendo su aislamiento entre sitios.

## Estructura prevista

```text
src/adminwp/                Paquete distribuible
  templates/admin/         Extensiones de las plantillas nativas
  templates/adminwp/       Componentes propios
  static/adminwp/          CSS, JavaScript e iconos distribuidos
  templatetags/            Integración con plantillas
assets/                    Fuentes Sass y JavaScript
tests/                     Pruebas de configuración e integración con Django
tests/browser/             Pruebas de navegador y regresión visual
demo/                      Proyecto de demostración con datos reproducibles
docs/                      Instalación, configuración y extensiones
tasks/                     Plan y lista de trabajo
```

## Orden de ejecución

```text
T01 Diseño y especificación
  -> T02 Instalación del paquete
  -> T03 Proyecto de demostración
  -> T04 Configuración y marca
  -> T05 Navegación con permisos
  -> T06 Apariencia y modos
  -> T07 Listados
  -> T08 Filtros y acciones
  -> T09 Formularios
  -> T10 Inlines
  -> T11 Widgets de relaciones
  -> T12 Resto de widgets
  -> T12.5 Portada propia y contraste de navegación
  -> T13 Páginas auxiliares
  -> T14 Varios sitios y extensiones
  -> T15 Accesibilidad y adaptación
  -> T16 Publicación verificable
```

Cada tarea entregará un recorrido verificable. Los archivos de `todo.md` son
una previsión; la especificación concretará las interfaces y los comandos antes
de ejecutar las tareas correspondientes. Si una tarea necesita más de cinco
archivos de implementación, se dividirá antes de empezar.

## Verificación prevista

- Pruebas de Django con pytest-django para configuración, renderizado, permisos
  y comportamiento del admin. Primero se fija el comportamiento mediante una
  prueba cuando se incorpora lógica nueva o se corrige un fallo.
- Pruebas en navegador para menú móvil, apariencia, formularios, acciones,
  autocompletado, popups e inlines añadidos dinámicamente.
- Regresión visual de las pantallas principales en claro y oscuro.
- Revisión de teclado, foco visible, etiquetas, contraste y movimiento reducido,
  con objetivo WCAG 2.2 AA para los componentes del tema.
- Instalación de un wheel en un entorno limpio y ejecución de `collectstatic`
  con almacenamiento de manifiesto; verificar que no faltan recursos.
- CI para las cuatro combinaciones Django/Python acordadas. Seguimiento de
  Django `main` informativo y separado del soporte publicado.

Los comandos previstos están definidos en SPEC.md y se habilitarán al preparar
el arnés de pruebas. Todavía no existen herramientas ni pruebas ejecutables del paquete.

## Hitos de entrega

| Hito | Tareas | Evidencia |
|---|---|---|
| Diseño revisable | T01 | Especificación, diseño y configuración pública coherentes |
| Alpha instalable | T02–T06 | Instalar, entrar y navegar con los tres modos |
| Beta funcional | T07–T13 | Recorridos CRUD y widgets nativos verificados |
| Candidata estable | T14–T15 | Extensiones, varios sitios y accesibilidad revisados |
| 1.0 | T16 | Paquete reproducible, documentación y matriz completa |

## Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| Conflictos entre Bootstrap y Django | Compilación selectiva y pruebas tempranas con widgets reales |
| Cambios de plantillas entre Django 6.0 y 6.1 | Herencia por bloques, pruebas en ambas series y adaptadores pequeños si hacen falta |
| Menús que muestran modelos no autorizados | Obtener permisos del sitio actual y probar usuarios con distintos permisos |
| Inlines o popups que dejan de funcionar | Conservar atributos y scripts nativos; probar creación y eliminación dinámicas |
| Modos visuales que divergen | Una preferencia común, sincronización con Bootstrap y pruebas del modo automático |
| Archivos ausentes del paquete | Instalar artefactos construidos y probar staticfiles fuera del checkout |
| Prometer compatibilidad futura sin evidencia | Declarar únicamente series verificadas y revisar cada nueva serie |

## Repositorio GitHub

El proyecto local está en
`/Users/crocha/projects/python/django/personal/django-adminwp`, tras mover la
carpeta original y verificar que se conservaron todos sus archivos.

El remoto `origin` está configurado como
`https://github.com/CARocha/django-adminwp.git`. Se verificó el acceso de lectura
al repositorio, que todavía no tiene referencias publicadas. La rama local es
`main`. El historial se mantendrá mediante commits locales; la publicación remota
se registrará cuando se realice.

La licencia y la disponibilidad del nombre para distribución se resolverán
antes de la publicación. No se publicará ningún artefacto por preparar el plan.

## Referencias

- https://github.com/barszczmm/django-wpadmin
- https://www.djangoproject.com/weblog/2025/apr/18/admin-theme-roundup/
- https://docs.djangoproject.com/en/6.0/ref/contrib/admin/
- https://docs.djangoproject.com/en/6.1/releases/6.1/
- https://getbootstrap.com/docs/5.3/customize/optimize/
- https://getbootstrap.com/docs/5.3/customize/color-modes/
- https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/apple/DESIGN.md
