# Accesibilidad y adaptación

NewAdmin conserva los controles y formularios de Django y añade foco visible,
navegación móvil, superficies con contraste y tablas desplazables. El objetivo es
WCAG 2.2 AA para sus componentes; esta alfa no es una certificación de conformidad.

## Navegación y teclado

- El primer enlace permite saltar al contenido principal.
- En escritorio, el botón lateral conserva el plegado y el filtro nativos.
- Hasta 767 px, el botón de navegación muestra el menú como una sección del flujo,
  sin tapar el contenido. Empieza cerrado en cada página y no modifica la
  preferencia de plegado del escritorio.
- Enter o Espacio activan el botón. Escape cierra el menú móvil y devuelve el foco.
  Si el filtro tiene texto, el primer Escape lo borra y el siguiente cierra el menú.
- Los enlaces ocultos quedan fuera del orden de tabulación. Las regiones de tablas
  admiten foco y desplazamiento horizontal cuando sus columnas lo requieren.

El diseño usa propiedades lógicas para RTL. La regresión de reflow cubre 320, 768,
1024 y 1440 píxeles CSS. Un viewport de 320 px comprueba el reflow equivalente a
una ventana de 1280 px con zoom del 400%; no sustituye probar el zoom real en los
navegadores y tecnologías de asistencia del proyecto consumidor.

## Apariencia

Los modos claro, oscuro y automático comparten tokens. Se respeta la preferencia
de movimiento reducido. El acabado de vidrio tiene un fondo opaco de respaldo,
se reduce con preferencias de transparencia reducida y se desactiva en colores
forzados. Los datos de gráficos también están disponibles como tablas HTML.

El tema añade nombres a los controles nativos de autocompletado y archivos que
los necesitan, incluidos nuevos inlines. Conserva las etiquetas y nombres
explícitos suministrados por el consumidor. Los iconos del menú son decorativos.

## Alcance de la verificación

Las pruebas de navegador ejecutan axe-core sobre login, portada genérica, listado,
formulario de artículo y cambio de contraseña en claro/oscuro. Otras pruebas
cubren dashboard con ECharts, errores de formularios, widgets, popups e inlines.
Se comprueban teclado, foco, RTL, reflow y preferencias de movimiento/transparencia.

No se ocultan infracciones de axe mediante exclusiones globales. Las comprobaciones
automáticas no garantizan una lectura correcta con todos los lectores de pantalla.
Revisa contenido, orden de lectura, zoom real y lectores de pantalla en tu proyecto.
Las personalizaciones, gráficos y widgets de terceros necesitan su propia auditoría.

El plegado/filtro de escritorio usa el almacenamiento nativo de Django; un
navegador que bloquee completamente localStorage/sessionStorage puede limitar
esos controles nativos. La apariencia del tema sí incluye un fallback sin storage.
