# Diseño de django-adminwp

Fecha: 2026-10-16. Estado: contrato visual propuesto para T01.
Especificación funcional: [SPEC.md](SPEC.md).

Revisión del 2026-10-17: el índice principal adopta la
[referencia de dashboard](docs/proposals/dashboard-v2.md) y la integración de
[Apache ECharts](docs/dashboard.md). El marco, la paleta y las acciones se comparten en
la portada y en los flujos CRUD. Login y popups conservan su disposición compacta.

## Dirección

Navegación de WordPress, claridad del admin nativo y superficies sobrias inspiradas
en la referencia Apple. La calidad debe apreciarse en listados, errores e inlines,
no solo en el dashboard. Dar espacio a la tarea y mantener información útil visible.

Sin tipografía remota obligatoria, galerías de marketing ni animación decorativa.
Una paleta inicial, sapphire, con variantes completas light y dark. Otras paletas
serán adiciones posteriores y deberán cumplir los mismos estados y contrastes.

## Tokens de color

Todos se publican con prefijo `--adminwp-`. Los valores son colores sólidos;
los contrastes de texto se miden sobre los fondos indicados.

| Token | Light | Dark |
|---|---|---|
| canvas | #F8F9FF | #11161D |
| surface | #FFFFFF | #1D2734 |
| surface-raised | #EFF4FF | #243244 |
| text | #0B1C30 | #EAF0F8 |
| text-muted | #536172 | #B2C0D2 |
| border | #DFE6F0 | #354359 |
| control-border | #858B93 | #7C8795 |
| primary | #141A23 | #EAF0F8 |
| primary-hover | #334259 | #FFFFFF |
| on-primary | #FFFFFF | #152032 |
| link | #141A23 | #EAF0F8 |
| focus | #141A23 | #EAF0F8 |
| sidebar | #EFF4FF | #161E29 |
| sidebar-text | #26364B | #DBE6F5 |
| sidebar-muted | #536172 | #A1B2CA |
| sidebar-active | #344760 | #A8BCE0 |
| sidebar-on-active | #FFFFFF | #152032 |
| success | #166534 | #8FDAA2 |
| success-bg | #EDF8F0 | #193322 |
| warning | #7A4B00 | #F4D18C |
| warning-bg | #FFF8E6 | #362D1E |
| danger | #B42318 | #FFB4A8 |
| danger-bg | #FFF2F0 | #3A1F21 |
| info | #075EA8 | #9ACBFF |
| info-bg | #EDF6FF | #1B2D40 |

Texto normal y texto de controles habilitados: mínimo 4.5:1. Bordes que permiten
identificar un control y foco respecto a la superficie adyacente: mínimo 3:1.
El token border es un separador decorativo, no el único límite de un input.
En navegación oscura, usar un anillo de foco claro que contraste con el fondo;
sobre una selección primaria, usar un anillo doble con separación.
Los estados no dependen solo de color: incluir texto, icono o indicación estructural.

Mapear estos tokens tanto a variables del admin nativo como a las de Bootstrap.
No cambiar solamente --bs-primary: botones, enlaces, hover, seleccionado y foco
deben estar vinculados al mismo sistema y tener sus propios estados.

## Tipografía y ritmo

- Fuente: system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif.
- Raíz 16 px; contenido administrativo 0.875 rem con line-height 1.5.
- Formularios móviles: inputs de al menos 1 rem; no deshabilitar zoom.
- Títulos de página: 1.75 rem/1.2, peso 600; secciones: 1.125 rem/1.4, peso 600.
- Ayuda: 0.8125 rem/1.5, con contraste de texto normal; no usar gris ilegible.
- Escala de espacio: 4, 8, 12, 16, 24, 32 y 48 px, expresada en rem.
- Radios: controles y paneles principales 4 px; widgets auxiliares 6–8 px. Evitar píldoras
  indiscriminadas que hagan botones y estados difíciles de distinguir.
- Sombra: reservada para menús flotantes y navegación superpuesta; las superficies
  principales se separan con fondo, espacio y bordes.

## Estructura y adaptación

```text
Barra superior: marca / acceso al sitio / usuario / apariencia
├─ Navegación: inicio, aplicaciones y modelos, enlaces adicionales
└─ Área de trabajo
   ├─ Breadcrumbs y título
   ├─ Mensajes y acciones de la página
   ├─ Listado, formulario o contenido nativo
   └─ Pie discreto
```

- Desde 768 px: lateral de 256 px incluyendo el botón de plegado de 23 px.
  Cabecera de 64 px; se conserva el plegado nativo.
- Bajo 768 px: se conserva la ocultación nativa del lateral. La navegación móvil
  superpuesta y su gestión de foco siguen pendientes de T15.
- Bajo 768 px: apilar herramientas y formularios cuando el marcado nativo lo permite.
- Contenido con padding 32 px en escritorio y 16 px en móvil; ancho fluido.
- Un scroll vertical principal; el menú puede desplazarse independientemente si
  excede la pantalla. Los popups no incluyen el marco de navegación completo.
- El documento no se desborda horizontalmente a 320 px. Tablas y widgets anchos
  usan un contenedor de desplazamiento propio con nombre accesible cuando haga falta.
- Mantener hasta 200% de zoom y comprobar reflow equivalente a 320 CSS px.
- RTL mediante propiedades lógicas; invertir disposición, no el significado de iconos.

### Marco compartido y portada

La plantilla base añade `adminwp-theme` a todas las páginas. El marco compartido
usa los tokens globales de la tabla anterior; ningún modo depende de una clase
exclusiva del dashboard. Las variables de Django y Bootstrap se resuelven en el
mismo ámbito para evitar que botones y widgets hereden la paleta anterior.

La cabecera usa la superficie principal, la marca y el lateral usan sidebar.
El título de la pantalla aparece en la cabecera cuando hay espacio. Login y
popups reciben los colores globales pero conservan su disposición compacta.
Las tipografías siguen siendo de sistema y no se solicitan fuentes remotas.

Sin proveedor, la portada muestra modelos autorizados y actividad reciente.
`ADMINWP.DASHBOARD` permite seleccionar un proveedor Python, su plantilla y Media,
con permisos verificados antes de preparar datos. La composición de referencia
expone un grid Bootstrap 8/4 desde 1200 px, con tabla posterior de ancho completo,
gutters de 32 px y gráfico principal de altura objetivo de 480 px.

La demo editorial cuenta entradas por categoría y estado, presenta minigráficos
con datos de los últimos siete días y ocho entradas recientes. Usa ECharts 6.1.0
local con su licencia Apache 2.0 y avisos de dependencias. Una instalación genérica
no hace consultas de negocio ni carga gráficos por omisión. Las tablas alternativas
son accesibles sin JavaScript. El alcance y uso están en [dashboard.md](docs/dashboard.md).

Objetivo pendiente de T15: el panel móvil moverá el foco a su interior y lo mantendrá mientras esté abierto,
cierra con Escape y devuelve el foco al botón de apertura. Sin JavaScript, el menú
permanece disponible en el flujo; los enlaces no dependen de hover.

## Componentes

### Navegación

Inicio seguido de aplicaciones con sus modelos y enlaces adicionales. Aplicación
actual abierta por defecto. Selección con fondo, texto y aria-current=page.
El botón de plegado informa su función y estado; en modo estrecho los iconos tienen
nombre accesible y una etiqueta que también aparece al recibir foco.

### Listados

Tablas reales con encabezados, selección reconocible y ordenación nativa. Filas
con altura objetivo de 44 px, permitiendo crecer con contenido multilínea.
Números alineados de forma coherente; URLs y textos largos no estiran el documento.
Filtros y herramientas mantienen sus valores y parámetros al navegar.
Un listado vacío explica el estado y muestra alta solo cuando existe permiso.

### Formularios

Preservar el orden semántico que entrega cada serie de Django. No reordenar con
CSS el contenido de ayuda y error. Campos relacionados visualmente juntos;
readonly claramente legible y sin apariencia de input editable.
Fieldsets plegables conservan details/summary nativos. Botones de guardado en flujo
normal, con acción principal clara y borrado separado. No usar un footer fijo que
oculte campos o errores.

### Inlines y widgets

Presentación consistente para tabulares y apilados. Las nuevas filas heredan los
estilos sin reinicializar toda la página. Los selectores múltiples, calendarios,
relojes y Select2 conservan controles, textos e IDs que esperan los scripts de Django.
Probar superposición y z-index dentro de navegación móvil y ventanas popup.

### Mensajes, errores y confirmaciones

Mensajes con icono, texto y estilo por nivel, incluyendo info y debug. Errores de
formulario visibles junto al campo y en el resumen nativo; enlaces/etiquetas
conservan relaciones accesibles. Confirmaciones de borrado muestran consecuencias,
objetos protegidos y cancelación con la misma claridad que la acción principal.

### Botones y controles

Hover, active, focus-visible y disabled definidos en ambos modos. Altura habitual
36 px para botones y 40 px para inputs; áreas táctiles de 44 px cuando corresponda.
Controles de icono de al menos 32 × 32 px y nombre accesible. Un control deshabilitado
no se representa como enlace operativo ni usa solo opacidad para explicar su estado.

## Integración CSS y recursos

- Conservar base.css y los estilos/widgets nativos necesarios.
- Extender las plantillas por bloques; overrides completos solo con una razón
  verificable y pruebas para las dos series de Django.
- No importar Reboot ni utilidades que colisionen con clases nativas sin revisión
  específica; incorporar grid/componentes Bootstrap a los componentes propios.
- Nunca redefinir globalmente todas las etiquetas input/select/button para imitar
  Bootstrap. Adaptar los selectores del admin dentro de su ámbito.
- Mantener CUSTOM_CSS al final, incluyendo después de estilos específicos de página;
  probar la cascada real de login, listado y formulario.
- Preferir los iconos SVG locales del admin donde ya existan. Los iconos de menú
  añadidos usan un subconjunto local de Bootstrap Icons con sus avisos de licencia.
- Transiciones de 120–180 ms para foco visual, plegado y panel; reducirlas a cero
  con prefers-reduced-motion. No animar cada fila ni la carga del formulario.

## Validación del diseño

Antes de declarar una pantalla terminada: verificar datos reales extensos, vacío,
errores, permisos restringidos, foco y los dos modos. Capturas comparables a
320, 768, 1024 y 1440 px; revisión manual de teclado, RTL y zoom. Los contrastes
calculados de tokens son evidencia parcial: estados y elementos renderizados
necesitan validación adicional en navegador.

## Verificación documental realizada

La auditoría documental de T01 se hizo con la paleta anterior. Sus resultados
numéricos no certifican los tokens actuales. La comprobación de contraste y foco
sobre las pantallas renderizadas sigue siendo parte de T15. La regresión del marco
compartido verifica paleta y geometría entre pantallas, tres modos y reflow a 320 px.

## Referencias de intención

- [django-wpadmin](https://github.com/barszczmm/django-wpadmin): navegación y familiaridad.
- [Referencia Apple](https://github.com/VoltAgent/awesome-design-md/blob/main/design-md/apple/DESIGN.md):
  sobriedad del color, tipografía y superficies, adaptadas a trabajo administrativo.
- [Modos de Bootstrap](https://getbootstrap.com/docs/5.3/customize/color-modes/).
