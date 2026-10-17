# Tareas de django-adminwp

Estado: plan aprobado. T01–T13.5 están implementadas; T14 continúa pendiente de cierre.
Plan: [plan.md](plan.md).

## T01 — Diseño y especificación
- [x] Definir `SPEC.md` y `DESIGN.md`, incluyendo estados claro/oscuro,
  configuración `ADMINWP`, extensión por sitio y política de compatibilidad.
- [x] Revisar coherencia del contrato y calcular contrastes de la paleta: 48 combinaciones verificadas.
- [x] Revisión de SPEC.md y DESIGN.md por el usuario antes de implementar.
- Aceptación: alcance y contratos sin ambigüedades; revisables antes de implementar.
- Verificación: contrastar requisitos del usuario con ambos documentos y revisar
  el plan detallado de la primera entrega.
- Dependencias: ninguna. Archivos: `SPEC.md`, `DESIGN.md`, `tasks/plan.md`, `tasks/todo.md`.

## T02 — Instalación del paquete
- [x] Preparar metadatos y aplicación Django instalable desde un wheel.
- Aceptación: Django descubre plantillas y recursos del paquete sin migraciones.
- Verificación: construir sdist/wheel, inspeccionarlos e instalar el wheel en un entorno limpio.
- Evidencia: pytest, Ruff, build sdist/wheel e instalación aislada del wheel con
  app, plantillas, Bootstrap compilado y JS descubiertos; matriz local Django 6.0/6.1
  × Python 3.13/3.14 con 20 pruebas aprobadas en cada combinación.
- Dependencias: T01. Archivos: `pyproject.toml`, `src/adminwp/__init__.py`,
  `src/adminwp/apps.py`, `tests/test_packaging.py`, `README.md`.

## T03 — Proyecto de demostración
- [x] Crear un proyecto reproducible con datos, modelos y permisos de muestra.
- Aceptación: se puede iniciar sesión y administrar objetos con el admin nativo.
- Verificación: comprobar configuración, migraciones de demo y un recorrido CRUD.
- Evidencia: `manage.py check`, migraciones y semilla funcionan; pruebas del admin
  crean, editan y borran artículos con un superusuario.
- Dependencias: T02. Archivos: `demo/manage.py`, `demo/config/settings.py`,
  `demo/config/urls.py`, `demo/catalog/models.py`, `demo/catalog/admin.py`.
- El scaffolding adicional y los datos se dividirán en tareas auxiliares pequeñas.

## Checkpoint A
- [x] Paquete instalable y demo reproducible; alcance revisado y aprobado.

## T04 — Configuración y marca
- [x] Incorporar valores predeterminados, validación de ajustes y marca del sitio.
- Aceptación: funciona sin `ADMINWP`; las opciones incorrectas producen errores claros.
- Verificación: pruebas de valores predeterminados, opciones inválidas y renderizado de marca.
- Evidencia: pruebas de valores predeterminados, merge de MENU, tipo/modo y rutas
  inválidas; título y cabecera personalizados aparecen en el login.
- Dependencias: T03. Archivos: `src/adminwp/conf.py`, `src/adminwp/checks.py`,
  `src/adminwp/templatetags/adminwp.py`, `src/adminwp/templates/admin/base_site.html`,
  `tests/test_configuration.py`.

## T05 — Navegación con permisos
- [x] Mostrar aplicaciones y modelos autorizados con menú plegable y activo actual.
- Aceptación: respeta permisos de vista/adición/cambio y enlaces del AdminSite actual.
- Verificación: pruebas con superusuario, staff restringido, permisos de solo vista
  y modelos con claves no numéricas; navegador para plegado y teclado.
- Evidencia: pruebas de orden, usuario con solo permiso de vista y elemento activo;
  Chrome verificó el toggle, su estado aria-expanded y el plegado nativos de Django.
- Dependencias: T04. Archivos: `src/adminwp/templatetags/adminwp.py`,
  `src/adminwp/templates/admin/nav_sidebar.html`, `src/adminwp/templates/admin/index.html`,
  `tests/test_navigation.py`.

## T06 — Apariencia y modos
- [x] Aplicar Bootstrap selectivo y tokens visuales al login, inicio y navegación.
- Aceptación: claro, oscuro y automático comparten una preferencia; los recursos
  compilados permiten usar el paquete sin herramientas frontend en destino.
- Verificación: construir recursos; probar cambio del sistema en modo automático,
  almacenamiento del navegador no disponible y capturas en ambos modos.
- Evidencia: CSS compilado selectivamente; pruebas JS cubren auto, ciclo del toggle,
  storage bloqueado y sincronización entre pestañas. Chrome confirmó ambos modos,
  el dashboard de escritorio y que el login no desborda a 320 px; `collectstatic`
  generó un manifiesto con todos los recursos del tema.
- Dependencias: T05. Archivos: `package.json`, `assets/scss/adminwp.scss`,
  `src/adminwp/static/adminwp/js/appearance.js`, `src/adminwp/templates/admin/base.html`,
  `tests/js/appearance.test.mjs`. Recursos generados se verifican en el artefacto.

## Checkpoint B
- [x] Instalar, iniciar sesión y navegar en móvil/escritorio con apariencia coherente.
- Evidencia: el navegador comprobó el flujo del admin en escritorio y a 320 px;
  la tabla desplaza dentro de su región accesible y el documento no se desborda.

## T07 — Listados
- [x] Adaptar tablas, búsqueda, ordenación y paginación conservando el marcado nativo.
- Aceptación: funcionan listados vacíos, columnas extensas y `list_editable` con errores.
- Verificación: navegador con búsqueda, paginación, ordenación y guardado válido/inválido.
- Evidencia: pruebas Django para estado vacío, 180 caracteres, búsqueda, orden ascendente,
  segunda página y error de `list_editable`; Playwright verificó scroll horizontal,
  búsqueda, segunda página, orden, guardado en línea y reflow a 320 px.
- Dependencias: T06. Archivos: `assets/scss/components/_changelist.scss`,
  `assets/scss/theme.scss`, `src/adminwp/templates/admin/change_list.html`,
  `tests/test_changelist.py`, `tests/browser/test_changelist.py`.

## T08 — Filtros y acciones
- [x] Presentar filtros, facetas y acciones masivas con comportamiento nativo.
- Aceptación: filtros y búsqueda conservan sus parámetros; las acciones respetan selección y permisos.
- Verificación: navegador con filtros combinados, acciones y selección en varias páginas.
- Evidencia: Playwright activó facetas, combinó status/categoría/búsqueda y ejecutó
  `delete_selected` sobre los 25 resultados de varias páginas; otra prueba confirma que
  un usuario de solo lectura no recibe esa acción. La vista móvil permanece dentro de 320 px.
- Dependencias: T07. Archivos: `assets/scss/components/_filters.scss`,
  `assets/scss/components/_actions.scss`, `src/adminwp/templates/admin/filter.html`,
  `tests/test_changelist.py`, `tests/browser/test_actions.py`.

## T09 — Formularios
- [x] Adaptar campos, fieldsets, ayuda, errores y botones de guardado.
- Aceptación: preservar orden accesible de cada serie de Django y campos de solo lectura.
- Verificación: crear/editar, errores de campo/formulario y fieldsets plegables en ambas series.
- Evidencia: Playwright verificó orden y plegado nativo, ayuda, error de campo,
  resaltado accesible del error, campos de solo lectura y superficies en claro/oscuro.
  27 pruebas de integración y 4 de navegador pasan con Django 6.0.9 y 6.1.2
  sobre Python 3.14.
- Dependencias: T08. Archivos: `assets/scss/components/_forms.scss`,
  `src/adminwp/templates/admin/change_form.html`, `tests/browser/test_forms.py`.

## Checkpoint C
- [ ] Recorridos de listado y formulario sin regresiones en la matriz Django/Python.

## T10 — Inlines
- [x] Adaptar inlines tabulares y apilados sin sustituir su lógica.
- Aceptación: añadir/eliminar filas conserva contadores, valores y errores.
- Verificación: guardar múltiples filas, borrar existentes y corregir errores dinámicos.
- Evidencia: Playwright creó filas tabulares y apiladas, eliminó un enlace existente,
  actualizó secciones, corrigió un error de validación y verificó scroll móvil y modos
  claro/oscuro. 27 pruebas de integración y 6 de navegador pasan con Django 6.0.9
  y 6.1.2 sobre Python 3.14.
- Dependencias: T09. Archivos: `assets/scss/components/_inlines.scss`,
  `tests/browser/test_inlines.py` y hasta dos plantillas específicas si son necesarias.

## T11 — Widgets de relaciones
- [x] Adaptar autocompletado, raw ID, selectores múltiples y popups nativos.
- Aceptación: relación seleccionada se devuelve al formulario; no hay una segunda copia de jQuery.
- Verificación: búsquedas, selección múltiple, popups e interacción dentro de nuevos inlines.
- Evidencia: Playwright confirmó búsqueda y selección de autocomplete, selector múltiple,
  popup raw ID dentro de un inline dinámico con retorno de categoría y cierre nativo,
  una sola copia de jQuery y presentación responsive en claro/oscuro. 27 pruebas de
  integración y 7 de navegador pasan en cada combinación de Django 6.0.9/6.1.2 y
  Python 3.13/3.14; Ruff, checks de Django, migraciones, recursos JS y build del paquete pasan.
- Dependencias: T10. Archivos: `assets/scss/components/_relations.scss`,
  `tests/browser/test_relations.py`, `demo/catalog/admin.py`, `demo/catalog/models.py`.

## T12 — Resto de widgets
- [x] Adaptar fechas, horas, archivos y textarea manteniendo los recursos `Media`.
- Aceptación: controles utilizables en ambos modos y widgets personalizados conservan sus recursos.
- Verificación: calendario/reloj, cambio de archivo y widget de prueba con CSS/JS propios.
- Evidencia: Playwright abrió calendario y reloj de Django en claro/oscuro, editó y guardó
  fecha, hora, textarea y archivo; confirmó el enlace y checkbox de archivo existente y
  reflow sin desbordamiento a 320 px. Una prueba de widget confirma que se acumulan los
  recursos CSS/JS personalizados con los recursos nativos. La subida de demo limita
  extensiones a TXT y tamaño a 5 MB, y usa un `MEDIA_ROOT` separado de los estáticos.
  38 pruebas pasan en cada combinación Django 6.0.9/6.1.2 × Python 3.13/3.14; Ruff,
  checks, migraciones, build CSS y pruebas JavaScript pasan.
- Dependencias: T11. Archivos: `assets/scss/components/_widgets.scss`,
  `tests/browser/test_widgets.py`, `tests/test_widgets.py`, `demo/catalog/models.py`.

## T12.5 — Portada y pulido de navegación
- [x] Crear una portada de trabajo propia y corregir el contraste de los módulos del menú.
- Aceptación: modelos agrupados en paneles según permisos; actividad reciente nativa;
  presentación clara/oscura y adaptación sin desbordamiento horizontal.
- Verificación: pruebas Django para accesos permitidos y actividad reciente; navegador
  para contraste, modos y vista de 320 px.
- Evidencia: 2 pruebas de integración y 1 de navegador pasan en cada combinación
  Django 6.0.9/6.1.2 × Python 3.13/3.14; captura de escritorio revisada. La portada
  usa aplicaciones/modelos y el registro nativo de Django, sin
  métricas ni llamadas externas; los fondos claros heredados del menú quedan transparentes.
- Dependencias: T12. Archivos: `src/adminwp/templates/admin/index.html`,
  `assets/scss/theme.scss`, `tests/test_dashboard.py`, `tests/browser/test_dashboard.py`.

## Checkpoint D
- [x] Widgets y formularios dinámicos probados antes de extender funcionalidad.
- [x] Portada y navegación revisadas visualmente antes de las páginas auxiliares.

## T13 — Páginas auxiliares
- [x] Completar historial, borrado, mensajes y cambio de contraseña.
- Aceptación: conservar confirmaciones, CSRF y cierre de sesión por POST.
- Verificación: pruebas Django y navegador para borrado individual/masivo y flujos de cuenta;
  confirmaciones y CSRF siguen presentes, y cerrar sesión continúa enviando POST.
- Evidencia: siete pruebas enfocadas y las 48 pruebas del suite pasan; Ruff y Django
  check pasan. El historial, la confirmación de borrado, los mensajes y el cambio
  de contraseña reciben el tema sin sustituir los flujos nativos de Django.
- Dependencias: T12.5. Archivos: `assets/scss/components/_auxiliary.scss`,
  `src/adminwp/templates/admin/object_history.html`,
  `src/adminwp/templates/registration/password_change_form.html`,
  `src/adminwp/templates/registration/password_change_done.html`,
  `tests/browser/test_auxiliary.py`, `tests/test_auxiliary.py`,
  `tests/test_authentication.py`.

## T13.5 — Dashboard extensible con Apache ECharts
- [x] Adaptar la referencia entregada a Bootstrap: lateral de 256 px, cabecera
  de 64 px, grid 8/4 y tabla de ancho completo en la portada.
- [x] Añadir Dashboard/EChartsDashboard, contexto por solicitud, permisos antes
  de consultar y configuración independiente por AdminSite.
- [x] Distribuir ECharts 6.1.0 local, con LICENSE/NOTICE y avisos de dependencias.
- [x] Implementar la demo con métricas reales, categorías y ocho entradas recientes.
- [x] Verificar claro/oscuro/auto, resize, movimiento reducido, datos sin JS,
  etiquetas con HTML y conservación de selección/zoom al cambiar de modo.
- Evidencia: 64 pruebas pasan en Django 6.0.9/6.1.2 × Python 3.13/3.14;
  4 pruebas JS, Ruff, Django check y builds pasan. Wheel instalado en un entorno
  ajeno al checkout y collectstatic con manifiesto verificados.
- Revisión independiente: corregida la pérdida de selección en gráficos circulares;
  regresión observada antes de la corrección y pasando después. La prueba de
  autorización detecta retirar el guard de permisos en una mutación temporal.
- Capturas claro/oscuro y móvil revisadas. La corrección T13.6 extiende el marco
  a todas las pantallas; la adaptación avanzada del menú móvil y la auditoría
  completa de accesibilidad siguen en T15.
- Guía de integración: [dashboard.md](../docs/dashboard.md).
- La T14 en curso se conserva en el stash `T14 menu extensions in progress before
  dashboard redesign`, asociado a `codex/site-extensions`, para retomarla sin perderla.

## T13.6 — Unificar el tema en todo el administrador
- [x] Mover paleta y marco de la portada a la base compartida.
- [x] Unificar cabecera, lateral, acciones y paneles en listados, formularios,
  índices de aplicación, historial, confirmaciones y contraseñas.
- [x] Conservar disposición compacta en login y popups con los mismos colores.
- [x] Adaptar cabeceras y flechas del selector múltiple al marcado de Django 6.0/6.1.
- Verificación: regresión de navegación entre pantallas en light/dark/auto,
  reflow a 320 px y pruebas existentes de CRUD, filtros, inlines y widgets.
- Evidencia: 68 pruebas pasan en las cuatro combinaciones Django 6.0.9/6.1.2 ×
  Python 3.13/3.14; cuatro pruebas JS, Ruff, Django check, build CSS y wheel/sdist
  pasan. El wheel incluye la base compartida, su CSS y la plantilla de contraseña.
- Revisión independiente: corregido y probado el desbordamiento de cabecera con
  un usuario de 84 caracteres; títulos consistentes en ambos marcados de Django.
- Capturas de formularios y listados en claro/oscuro revisadas. Los datos y flujos
  nativos de Django permanecen cubiertos por las pruebas funcionales existentes.

## T13.7 — Acabado de vidrio sutil
- [x] Añadir vidrio en cabecera y barra de guardado, con reflejos y sombras en
  tarjetas exteriores, y variaciones estáticas muy suaves en el lienzo.
- [x] Mantener campos, tablas y gráficos sin desenfoque; evitar sombras duplicadas
  en los minigráficos de métricas. Reducir blur a 8 px en móvil.
- [x] Partir de superficies opacas y activar blur mediante detección de soporte.
  Respetar reducción de transparencias y colores forzados.
- Verificación: capturas claro/oscuro y móvil; prueba de la preferencia real del
  navegador para recuperar fondos opacos y eliminar blur.
- Evidencia: 70 pruebas pasan en Django 6.0.9/6.1.2 × Python 3.13/3.14;
  cuatro pruebas JS, Ruff, Django check, build CSS y wheel/sdist pasan.
- Revisión independiente de cascada, compatibilidad de widgets y capturas completada.
  Las tarjetas interiores de minigráficos quedan exentas de sombra adicional.

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
