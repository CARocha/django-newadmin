# Tareas de django-adminwp

Estado: plan aprobado. T01 tiene documentos escritos y revisión documental realizada;
su revisión por el usuario está pendiente. T02–T16 no se han iniciado.
Plan: [plan.md](plan.md).

## T01 — Diseño y especificación
- [x] Definir `SPEC.md` y `DESIGN.md`, incluyendo estados claro/oscuro,
  configuración `ADMINWP`, extensión por sitio y política de compatibilidad.
- [x] Revisar coherencia del contrato y calcular contrastes de la paleta: 48 combinaciones verificadas.
- [ ] Revisión de SPEC.md y DESIGN.md por el usuario antes de implementar.
- Aceptación: alcance y contratos sin ambigüedades; revisables antes de implementar.
- Verificación: contrastar requisitos del usuario con ambos documentos y revisar
  el plan detallado de la primera entrega.
- Dependencias: ninguna. Archivos: `SPEC.md`, `DESIGN.md`, `tasks/plan.md`, `tasks/todo.md`.

## T02 — Instalación del paquete
- [ ] Preparar metadatos y aplicación Django instalable desde un wheel.
- Aceptación: Django descubre plantillas y recursos del paquete sin migraciones.
- Verificación: construir sdist/wheel, inspeccionarlos e instalar el wheel en un entorno limpio.
- Dependencias: T01. Archivos: `pyproject.toml`, `src/adminwp/__init__.py`,
  `src/adminwp/apps.py`, `tests/test_packaging.py`, `README.md`.

## T03 — Proyecto de demostración
- [ ] Crear un proyecto reproducible con datos, modelos y permisos de muestra.
- Aceptación: se puede iniciar sesión y administrar objetos con el admin nativo.
- Verificación: comprobar configuración, migraciones de demo y un recorrido CRUD.
- Dependencias: T02. Archivos: `demo/manage.py`, `demo/config/settings.py`,
  `demo/config/urls.py`, `demo/catalog/models.py`, `demo/catalog/admin.py`.
- El scaffolding adicional y los datos se dividirán en tareas auxiliares pequeñas.

## Checkpoint A
- [ ] Paquete instalable y demo reproducible; revisar alcance antes de cambiar el admin.

## T04 — Configuración y marca
- [ ] Incorporar valores predeterminados, validación de ajustes y marca del sitio.
- Aceptación: funciona sin `ADMINWP`; las opciones incorrectas producen errores claros.
- Verificación: pruebas de valores predeterminados, opciones inválidas y renderizado de marca.
- Dependencias: T03. Archivos: `src/adminwp/conf.py`, `src/adminwp/checks.py`,
  `src/adminwp/templatetags/adminwp.py`, `src/adminwp/templates/admin/base_site.html`,
  `tests/test_configuration.py`.

## T05 — Navegación con permisos
- [ ] Mostrar aplicaciones y modelos autorizados con menú plegable y activo actual.
- Aceptación: respeta permisos de vista/adición/cambio y enlaces del AdminSite actual.
- Verificación: pruebas con superusuario, staff restringido, permisos de solo vista
  y modelos con claves no numéricas; navegador para plegado y teclado.
- Dependencias: T04. Archivos: `src/adminwp/navigation.py`,
  `src/adminwp/templates/admin/nav_sidebar.html`, `assets/js/navigation.js`,
  `tests/test_navigation.py`, `tests/browser/test_navigation.py`.

## T06 — Apariencia y modos
- [ ] Aplicar Bootstrap selectivo y tokens visuales al login, inicio y navegación.
- Aceptación: claro, oscuro y automático comparten una preferencia; los recursos
  compilados permiten usar el paquete sin herramientas frontend en destino.
- Verificación: construir recursos; probar cambio del sistema en modo automático,
  almacenamiento del navegador no disponible y capturas en ambos modos.
- Dependencias: T05. Archivos: `package.json`, `assets/scss/adminwp.scss`,
  `assets/js/appearance.js`, `src/adminwp/templates/admin/base.html`,
  `tests/browser/test_appearance.py`. Recursos generados se verifican en el artefacto.

## Checkpoint B
- [ ] Instalar, iniciar sesión y navegar en móvil/escritorio con apariencia coherente.

## T07 — Listados
- [ ] Adaptar tablas, búsqueda, ordenación y paginación conservando el marcado nativo.
- Aceptación: funcionan listados vacíos, columnas extensas y `list_editable` con errores.
- Verificación: navegador con búsqueda, paginación, ordenación y guardado válido/inválido.
- Dependencias: T06. Archivos: `assets/scss/components/_changelist.scss`,
  `src/adminwp/templates/admin/change_list.html`, `tests/browser/test_changelist.py`.

## T08 — Filtros y acciones
- [ ] Presentar filtros, facetas y acciones masivas con comportamiento nativo.
- Aceptación: filtros y búsqueda conservan sus parámetros; las acciones respetan selección y permisos.
- Verificación: navegador con filtros combinados, acciones y selección en varias páginas.
- Dependencias: T07. Archivos: `assets/scss/components/_filters.scss`,
  `src/adminwp/templates/admin/filter.html`, `tests/browser/test_actions.py`.

## T09 — Formularios
- [ ] Adaptar campos, fieldsets, ayuda, errores y botones de guardado.
- Aceptación: preservar orden accesible de cada serie de Django y campos de solo lectura.
- Verificación: crear/editar, errores de campo/formulario y fieldsets plegables en ambas series.
- Dependencias: T08. Archivos: `assets/scss/components/_forms.scss`,
  `src/adminwp/templates/admin/change_form.html`, `tests/browser/test_forms.py`.

## Checkpoint C
- [ ] Recorridos de listado y formulario sin regresiones en la matriz Django/Python.

## T10 — Inlines
- [ ] Adaptar inlines tabulares y apilados sin sustituir su lógica.
- Aceptación: añadir/eliminar filas conserva contadores, valores y errores.
- Verificación: guardar múltiples filas, borrar existentes y corregir errores dinámicos.
- Dependencias: T09. Archivos: `assets/scss/components/_inlines.scss`,
  `tests/browser/test_inlines.py` y hasta dos plantillas específicas si son necesarias.

## T11 — Widgets de relaciones
- [ ] Adaptar autocompletado, raw ID, selectores múltiples y popups nativos.
- Aceptación: relación seleccionada se devuelve al formulario; no hay una segunda copia de jQuery.
- Verificación: búsquedas, selección múltiple, popups e interacción dentro de nuevos inlines.
- Dependencias: T10. Archivos: `assets/scss/components/_relations.scss`,
  `tests/browser/test_relations.py`, `demo/catalog/admin.py`.

## T12 — Resto de widgets
- [ ] Adaptar fechas, horas, archivos y textarea manteniendo los recursos `Media`.
- Aceptación: controles utilizables en ambos modos y widgets personalizados conservan sus recursos.
- Verificación: calendario/reloj, cambio de archivo y widget de prueba con CSS/JS propios.
- Dependencias: T11. Archivos: `assets/scss/components/_widgets.scss`,
  `tests/browser/test_widgets.py`, `tests/widgets.py`.

## Checkpoint D
- [ ] Widgets y formularios dinámicos probados antes de extender funcionalidad.

## T13 — Páginas auxiliares
- [ ] Completar historial, borrado, mensajes y cambio de contraseña.
- Aceptación: conservar confirmaciones, CSRF y cierre de sesión por POST.
- Verificación: navegador para borrado individual/masivo y flujos de cuenta.
- Dependencias: T12. Archivos: `assets/scss/components/_auxiliary.scss`,
  `tests/browser/test_auxiliary.py`, `tests/test_authentication.py`.

## T14 — Varios sitios y extensiones
- [ ] Incorporar configuración por AdminSite, menú personalizado y CSS adicional.
- Aceptación: sitios con namespaces distintos no mezclan enlaces ni configuración;
  plantillas del consumidor y `Media` siguen funcionando.
- Verificación: pruebas con dos sitios, permisos diferentes y overrides del consumidor.
- Dependencias: T13. Archivos: `src/adminwp/conf.py`, `src/adminwp/navigation.py`,
  `tests/test_sites.py`, `tests/test_extensions.py`, `docs/configuration.md`.

## T15 — Accesibilidad y adaptación
- [ ] Revisar teclado, foco, contraste, RTL, zoom y vistas móviles.
- Aceptación: navegación operable sin ratón, foco visible, tablas desplazables y
  controles accesibles en claro/oscuro; objetivo WCAG 2.2 AA para componentes propios.
- Verificación: pruebas automáticas de accesibilidad y revisión manual de los recorridos principales.
- Dependencias: T14. Archivos: `assets/scss/components/_responsive.scss`,
  `assets/scss/components/_accessibility.scss`, `tests/browser/test_accessibility.py`,
  `tests/browser/test_responsive.py`, `docs/accessibility.md`.

## Checkpoint E
- [ ] Revisar integración y accesibilidad; registrar limitaciones reales antes de publicar.

## T16 — Publicación verificable
- [ ] Preparar CI, documentación de instalación y validación del paquete candidato.
- Aceptación: cuatro combinaciones Django/Python verificadas; wheel instalado fuera
  del checkout; `collectstatic` con manifiesto funciona sin recursos faltantes.
- Verificación: matriz de CI, instalación limpia, pruebas de navegador y revisión de
  contenido de wheel/sdist; publicación en PyPI como acción posterior explícita.
- Dependencias: T15. Archivos: `.github/workflows/ci.yml`, `docs/installation.md`,
  `docs/extensions.md`, `tests/test_distribution.py`, `CHANGELOG.md`.

## Checkpoint final
- [ ] Todos los criterios anteriores verificados; documentación y limitaciones coherentes.
- [ ] Revisión del candidato y decisión de publicación con el usuario.
