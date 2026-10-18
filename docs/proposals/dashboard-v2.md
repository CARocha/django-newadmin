# Dashboard NewAdmin: revisión visual y extensión con datos propios

Fecha: 2026-10-17. Estado: primera iteración implementada; biblioteca ECharts confirmada por el usuario.

Esta propuesta responde a la referencia proporcionada en
`stitch_fleet_admin_dashboard/`: `screen.png`, `code.html` y `DESIGN.md`.
Los nombres y contenidos de logística son ilustrativos. El producto sigue siendo
django-newadmin, construido sobre Bootstrap y el administrador nativo de Django.

## Resultado esperado

Un panel de trabajo con las proporciones, densidad y jerarquía de la referencia:
navegación lateral clara en modo claro, cabecera compacta, una visualización
dominante, métricas secundarias y tablas útiles. En modo oscuro cambia el sistema
de superficies y contraste, manteniendo la misma composición.

El proyecto consumidor debe poder escribir Python para consultar sus modelos,
registrar ese contenido como panel principal y usar componentes de presentación
del tema. La instalación básica seguirá mostrando un escritorio útil sin exigir
que se definan gráficos ni se instalen herramientas de frontend.

## Qué aporta la referencia y qué hay que reconstruir

El HTML usa Tailwind por CDN, fuentes de Google, imágenes externas y datos de
ejemplo. El mapa es una imagen y las barras pequeñas son elementos HTML. No hay
una biblioteca de gráficos ni lógica funcional para buena parte de los controles.

Se trasladarán la composición y las medidas a Bootstrap 5.3, plantillas Django,
SCSS y JavaScript del paquete. La maqueta no se añadirá como una página independiente
ni se incorporará Tailwind al proyecto.

El documento recibido contiene criterios que difieren de su propia captura/HTML:
prohíbe separadores mientras la maqueta los utiliza; propone márgenes de 80–96 px
frente a los 32 px del HTML; describe métricas sin contenedor y muestra tarjetas.
Para resolver esas diferencias, las proporciones del HTML y la composición de la
captura son la referencia principal. Las reglas de contraste y usabilidad del
producto prevalecen sobre consignas como eliminar todos los bordes.

## Contrato visual propuesto

Las medidas siguientes son píxeles CSS, no medidas del archivo de imagen exportado.

| Elemento | Escritorio | Adaptación |
|---|---|---|
| Navegación lateral | 256 px expandida | Panel desplegable bajo 992 px |
| Cabecera de contenido | 64 px de altura objetivo | Puede crecer al envolver controles o ampliar texto |
| Área de trabajo | Ancho máximo de 1600 px, centrada en el espacio disponible | Ancho fluido en tamaños menores |
| Padding del área de trabajo | 32 px | 24 px en tablet y 16 px en móvil |
| Separación de los bloques principales | 32 px | 24/16 px según tamaño |
| Bloque principal | 8 de 12 columnas Bootstrap desde 1200 px | Ancho completo por debajo |
| Columna de métricas | 4 de 12 columnas desde 1200 px; dos paneles apilados | Dos columnas cuando quepan y una en móvil |
| Visualización principal | Altura objetivo de 480 px en escritorio | Altura adaptada; sin recortar contenido por una altura fija |
| Tabla inferior | 12 columnas | Desplazamiento horizontal dentro de la tabla |
| Radios | 2–4 px en paneles y controles | Los mismos en ambos modos |
| Texto de datos | 14 px, interlineado cómodo, números tabulares | Sin etiquetas diminutas para información esencial |
| Cifras principales | 36–44 px | Reducir cuando el dato no quepa |

El grid será de Bootstrap. Los gutters se ajustarán a 32 px mediante las variables
del grid; no se añadirá un segundo sistema de layout para los mismos paneles.

### Superficies, color y tipografía

- Modo claro: fondo muy suave próximo a `#f8f9ff`, lateral próximo a `#eff4ff`,
  paneles blancos, texto principal próximo a `#0b1c30` y selección en carbón.
- Modo oscuro: fondo próximo a `#11161d`, lateral `#161e29`, paneles `#1d2734`
  y texto claro; los valores definitivos necesitan medir contraste renderizado.
- Los estados usan verde, ámbar y rojo con texto o icono. Una variación positiva
  numérica no implica automáticamente que el indicador sea favorable.
- Bordes discretos cuando aporten lectura, límites de controles visibles y foco
  de alto contraste. No se copiarán las etiquetas de 10 px de la maqueta.
- Manrope para títulos e Inter para datos son una opción fiel a la referencia:
  distribuirlas localmente exige comprobar y conservar sus licencias. Siempre
  habrá fallback a fuentes de sistema y ninguna petición a Google Fonts.
- Los colores se expresarán mediante tokens de NewAdmin, mapeados a Django y
  Bootstrap. Este cambio de dirección requiere revisar el contrato actual de
  `PALETTE` antes de convertir estos colores en valores de ejecución.

La nueva dirección sustituiría la portada de tarjetas uniformes y el lateral
siempre oscuro del diseño anterior. Se revisará el marco compartido en listados
y formularios para que el usuario no encuentre dos estilos distintos al navegar.

## Composición de la demostración editorial

```text
┌────────────────┬──────────────────────────────────────────────────────┐
│ Marca          │ Panel principal                 Apariencia · Cuenta │
│ Inicio         ├──────────────────────────────────┬───────────────────┤
│ Aplicaciones   │ Entradas por categoría           │ Publicadas        │
│ Modelos        │                                  ├───────────────────┤
│ Enlaces propios│ Gráfico principal                │ Borradores        │
│                ├──────────────────────────────────┴───────────────────┤
│                │ Últimas entradas · Categoría · Estado · Fecha       │
│                │ Acciones reales según permisos · Ver todas          │
│                ├──────────────────────────────────────────────────────┤
│                │ Accesos a modelos / Actividad reciente               │
└────────────────┴──────────────────────────────────────────────────────┘
```

En la demo se usarán `Article` y `Category`, que ya existen. El gráfico contará
entradas por su categoría principal; los artículos sin categoría tendrán una
etiqueta explícita. Las métricas serán cantidades reales de publicaciones y
borradores. Las tendencias se mostrarán únicamente si hay dos periodos reales
comparables. La tabla mostrará una cantidad acotada de entradas recientes y
enlaces a las vistas nativas, en lugar de una paginación decorativa.

Una instalación genérica no puede deducir qué significa «publicado», qué modelo
representa ventas o qué datos pertenecen a cada organización. Sin proveedor propio,
mostrará los modelos autorizados y la actividad del usuario con el mismo lenguaje
visual, sin contadores de negocio inventados ni consultas a todos los modelos.

Los controles visibles tendrán una función real. La cabecera inicial conservará
los accesos al sitio, cuenta y apariencia. Una búsqueda global, notificaciones o
un menú de ayuda adicional solo se mostrarán si existe una integración que los
haga funcionar.

## Extensión del panel: propuesta de interfaz pública

Se propone un proveedor Python por panel, seleccionado mediante una ruta importable
en `NEWADMIN`. Es una interfaz nueva que debe quedar documentada y probada antes de
publicarla. El siguiente ejemplo ilustra la interfaz implementada:

```python
NEWADMIN = {
    "DASHBOARD": "news.admin_dashboard.NewsDashboard",
    "SITES": {
        "operations": {
            "DASHBOARD": "operations.admin_dashboard.OperationsDashboard",
        },
    },
}
```

```python
from newadmin.dashboard import Dashboard


class NewsDashboard(Dashboard):
    template_name = "news/admin/dashboard.html"
    permissions = ("news.view_article",)

    def get_context_data(self, request):
        # Función del proyecto que consulta sus modelos y aplica su alcance.
        return build_news_dashboard_context(request)
```

Este proveedor cumple la función de una vista de contenido del panel: recibe la
solicitud autenticada y prepara el contexto. El punto de entrada sigue siendo el
índice protegido del AdminSite. No hace falta registrar otra URL pública ni
reemplazar los registros existentes de ModelAdmin.

El renderizador comprueba `permissions` antes de ejecutar el proveedor. Si el usuario
no dispone de esos permisos, muestra el escritorio genérico con sus propios accesos
autorizados. Los paneles con permisos distintos se separarán en bloques que el
proveedor evalúe de forma condicional; los ejemplos deben comprobar permisos antes
de consultar cada conjunto de datos.

### Qué ofrecerá el tema

- Una plantilla base de dashboard con zonas de bloque principal, métricas,
  tablas y contenido secundario. El desarrollador puede reemplazar esas zonas.
- Componentes de presentación para métrica, tabla y panel de gráfico; conservan
  sus tamaños, estados vacíos, títulos y estilos en ambos modos.
- Contexto nativo de Django disponible para la plantilla, con una clave propia
  para el contexto de negocio, evitando sobrescribir datos de permisos o sesión.
- Recursos CSS/JS del proveedor mediante `Media`, combinados sin duplicados.
  Los recursos se cargan únicamente en las páginas que los utilizan.
- Resolución del proveedor por nombre de AdminSite; un sitio no comparte sus
  datos, opciones ni enlaces con otro por accidente.
- Personalización progresiva: instalar el tema; luego añadir un proveedor y su
  plantilla únicamente si el proyecto necesita un panel de negocio.

Las tablas se renderizarán con HTML semántico y Bootstrap. El proveedor es responsable
de las consultas, el alcance por usuario/organización y sus reglas de negocio. Un
permiso de modelo por sí solo no garantiza ese alcance. Los ejemplos aplicarán
los filtros antes de hacer agregaciones y limitarán las filas de las tablas.

Para «entradas por categoría», una vez obtenido el queryset autorizado `articles`,
la agregación es una consulta ordinaria del ORM:

```python
articles.values("category__name").annotate(total=Count("pk"))
```

El adaptador de gráficos recibe los resultados ya calculados. No interpreta
nombres arbitrarios de modelos/campos para construir consultas automáticas.

## Apache ECharts: biblioteca elegida

Decisión confirmada por el usuario el 2026-10-17: usar Apache ECharts. Su licencia
Apache 2.0 permite distribuir los recursos locales con el tema, conservando
LICENSE y NOTICE. No se requiere una licencia comercial de gráficos al consumidor.
[Licencia oficial](https://github.com/apache/echarts/blob/master/LICENSE).

Bootstrap sigue resolviendo el marco, las tarjetas y las tablas. ECharts se carga
únicamente en proveedores que extiendan `EChartsDashboard`. Los datos se entregan
con `json_script`, se dibujan mediante SVG y conservan una tabla HTML alternativa.
Se sincronizan los colores con el modo resuelto light/dark/auto de NewAdmin.

La biblioteca se fija en package-lock.json y sus recursos compilados se incluyen
en el wheel junto con su licencia y avisos; instalar el paquete no exige Node.
El adaptador no utiliza servicios externos, eval ni tooltips HTML. Los gráficos
respetan la preferencia de movimiento reducido y se redimensionan con su panel.
No se presupone accesibilidad completa por activar ARIA: la tabla alternativa,
el teclado y el foco se verifican en el navegador.

Los proyectos pueden reutilizar `Dashboard` para paneles sin gráficos o
`EChartsDashboard` para los tipos de gráficos de ECharts. No hace falta un wrapper
Python: Django prepara los datos y JavaScript los presenta.

## Orden de trabajo propuesto

1. **Nueva base visual.** Revisar los apartados de diseño y alcance anteriores,
   sustituir sus valores en DESIGN.md/SPEC.md y ajustar lateral, cabecera, tipografía,
   superficies y separación. Primer resultado revisable: capturas claro/oscuro
   comparables con la referencia, con navegación nativa operativa.
2. **Panel principal.** Implementar la composición 8/4 + tabla y el escritorio
   genérico de la misma familia visual. Verificar los tamaños antes de ampliar
   funcionalidades del admin.
3. **Proveedor y componentes.** Especificar y probar la interfaz de dashboard,
   los bloques de plantilla, permisos, alcance por sitio y recursos `Media`.
4. **Integración ECharts.** Añadir el adaptador local y la demo editorial
   con datos reales, tabla alternativa y guía de uso y avisos de licencia.
5. **Revisión integrada.** Navegador real para dashboard, listado, formulario,
   inlines y widgets; controles de cuenta, permisos y CSP; documentación de uso.

La T14 de extensiones ya tiene cambios en curso. Se conservarán y se integrarán
solo después de validarlos; este rediseño pasa a ser la prioridad visual solicitada.
La T15 de accesibilidad y la T16 de publicación siguen siendo necesarias.

## Criterios para aceptar el resultado

- Comparación visual con la referencia, usando los mismos tamaños de viewport.
- Capturas en claro y oscuro a 1440 y 1920 px; revisión de reflow a 320, 768 y
  1024 px. Sin desbordamiento horizontal del documento.
- Ninguna métrica de ejemplo hardcodeada en el tema de producción.
- Datos de la demo coherentes con la base de datos; cambios en las entradas
  se reflejan en las métricas, las categorías y la tabla.
- Un usuario restringido no dispara consultas de un panel no autorizado ni recibe
  sus datos en HTML o JSON. Un segundo AdminSite mantiene sus propios resultados.
- Gráficos que cambian con light/dark/auto, legibles mediante teclado y con tabla
  alternativa. Datos con etiquetas largas, ceros y ausencia de registros cubiertos.
- Fuentes y recursos locales; ausencia de elementos de logística o marca de la maqueta.
- CRUD, acciones, inlines, widgets y cierre de sesión siguen superando sus pruebas.
- API pública y ejemplos de configuración comprobados antes de publicar una alfa.

## Referencias técnicas consultadas

- [Grid de Bootstrap 5.3](https://getbootstrap.com/docs/5.3/layout/grid/).
- [Apache ECharts](https://echarts.apache.org/en/index.html).
- [Licencia ECharts](https://github.com/apache/echarts/blob/master/LICENSE).
- [Temas ECharts](https://echarts.apache.org/handbook/en/concepts/style/).
- [ARIA ECharts](https://echarts.apache.org/handbook/en/best-practices/aria/).
