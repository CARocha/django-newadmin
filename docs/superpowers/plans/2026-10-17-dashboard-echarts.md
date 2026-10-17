# Dashboard con Apache ECharts

> Ejecución nativa e incremental en esta sesión mediante superpowers:executing-plans.

**Objetivo:** ofrecer un dashboard de Bootstrap con datos propios, gráficos ECharts
locales, dos modos y la composición editorial solicitada.

**Arquitectura:** proveedor por solicitud seleccionado por `ADMINWP.DASHBOARD`,
con permisos previos a las consultas, plantilla propia y `Media` de Django.
`EChartsDashboard` añade los recursos locales del adaptador. La demo usa el ORM
de sus propios modelos; el paquete no conoce los modelos del consumidor.

**Stack:** Django 6.0/6.1, Python 3.13/3.14, Bootstrap 5.3.8, ECharts 6.1.0.
**Diseño:** [dashboard-v2.md](../../proposals/dashboard-v2.md).

## Límites y revisión

- Sin migraciones, middleware ni AdminSite obligatorio adicional para el consumidor.
- Sin código remoto ni Highcharts; LICENSE/NOTICE de ECharts incluidos.
- Mantener el escritorio genérico sin consultas de negocio y sin JS de gráficos.
- Revisar acceso de solo vista, datos por sitio, datos vacíos, etiquetas maliciosas
  y etiquetas largas antes de considerar el panel listo.
- T14 en curso conservada en un stash identificado; no mezclar cambios incompletos.

## 1. Proveedor de dashboard

- [x] Crear pruebas de integración en `tests/test_dashboard_provider.py` que fallen
  sin `ADMINWP.DASHBOARD`: plantilla configurada, permisos antes de consultar,
  contexto aislado, recursos una sola vez y selección independiente por sitio.
- [x] Implementar `Dashboard`, `EChartsDashboard` y
  `resolve_dashboard(request)` en `src/adminwp/dashboard.py`.
  `get_context_data(request)` devuelve un mapping; `permissions` es una secuencia
  de permisos; `template_name` identifica una plantilla de contenido.
- [x] Cachear únicamente en la solicitud; sin caché de datos entre usuarios.
- [x] Añadir `DASHBOARD=None` a `conf.py` y la validación de rutas importables.
- [x] Añadir tags para resolver el panel y renderizar su Media con nonce nativo.
- [x] Integrar el proveedor en `templates/admin/index.html`; conservar el fallback.
- [x] Ejecutar pruebas del proveedor y configuración; guardar el incremento verificado.

## 2. Recursos locales y adaptador ECharts

- [x] Fijar ECharts en npm y crear `scripts/build-charts.mjs` para copiar su
  distribución compilada, LICENSE y NOTICE al paquete.
- [x] Implementar `dashboard-charts.js`: JSON no ejecutable, SVG, tooltip de texto,
  colores por modo resuelto, resize y movimiento reducido.
- [x] Crear `templates/adminwp/dashboard/chart.html`: título, contenedor y tabla
  alternativa con datos escapados; conservar la tabla cuando no hay JavaScript.
- [x] Probar SVG real, cambios de tema, ancho móvil, ausencia de red externa,
  etiquetas con HTML y dos gráficos simultáneos en `tests/browser/test_charts.py`.
- [x] Verificar build y que LICENSE/NOTICE aparecen en los recursos de distribución.

## 3. Composición y demo editorial

- [x] Crear `templates/adminwp/dashboard/layout.html` y `_dashboard.scss`:
  Bootstrap 8/4 + tabla, padding/gutters 32 px, radio pequeño, métricas legibles,
  estados vacíos y modos completos.
- [x] Adaptar el marco compartido con tokens y selectores acotados: sidebar 256 px,
  cabecera 64 px, lateral claro en light y oscuro en dark. Verificar las pantallas
  existentes afectadas, sin cambiar su semántica.
- [x] Crear `demo/catalog/dashboard.py` con proveedor editorial: contar categorías,
  publicaciones y borradores desde un queryset autorizado, y listar ocho entradas.
- [x] Configurar el proveedor solo en la demo; no cambiar el valor por defecto.
- [x] Pruebas con registros reales y valores actualizados, sin consultas de N+1.
- [x] Revisar capturas de escritorio y móvil de los dos modos y corregir la cascada.

## 4. Documentación y cierre

- [x] Documentar registro, herencia de plantilla, permisos, Media, opciones del
  gráfico, tabla alternativa y alcance del queryset en `docs/dashboard.md`.
- [x] Actualizar DESIGN/SPEC y tareas con el alcance real y la decisión ECharts.
- [x] Ejecutar pytest, Ruff, Django check, build CSS/JS y comprobar wheel/sdist.
- [x] Revisar el diff completo y las capturas, registrar limitaciones y guardar
  commits verificados. Integrar en main con el flujo local autorizado.

## Resultado y decisiones registradas

- Tareas 1–4 implementadas. 64 pruebas pasan en las cuatro combinaciones de la matriz;
  Ruff, cuatro pruebas JS, Django check, build CSS y build de recursos pasan.
- Wheel construido desde sdist, instalado fuera del checkout y validado con
  collectstatic/ManifestStaticFilesStorage, incluyendo avisos de dependencias.
- Revisión independiente: se corrigió y probó selección de series al cambiar de tema.
- Ruling: la base visual nueva se limita al índice principal durante esta iteración;
  aplicar sus tokens globalmente a CRUD requiere la revisión T15 y no se declara terminado.
- Ruling: conservar fuentes de sistema ahora mantiene la instalación sin red ni nuevas
  fuentes distribuidas; la referencia visual se interpreta mediante proporciones y jerarquía.
- Ruling: distribuir el runtime completo de ECharts admite los tipos de gráficos del
  consumidor sin otro builder; cuesta aproximadamente 1.1 MB minificado, cargado solo
  por proveedores ECharts. Se conservan todos sus avisos de dependencias.
- Permisos: una mutación temporal que eliminaba el guard fue detectada por el test;
  el archivo fue restaurado y la prueba volvió a pasar antes de guardar los cambios.
