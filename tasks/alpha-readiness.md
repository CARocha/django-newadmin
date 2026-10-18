# Cierre de la primera alfa — 2026-10-17

Contrato: T15/T16 de todo.md y criterios AC01–AC11 de SPEC.md. Conservar
el diseño aprobado, Bootstrap y los comportamientos del admin. Licencia del
proyecto: BSD de 3 cláusulas, elegida por el usuario.

1. T15: auditar páginas con axe-core, teclado, RTL y anchos 320/768/1024/1440;
   corregir navegación móvil y foco, verificar almacenamiento y zoom/reflow.
2. T16 documentación: Sphinx + MyST para integrar Markdown existente; guías
   de instalación, configuración, extensiones, accesibilidad y publicación.
   Compilación estricta y ejemplos de instalación verificados.
3. T16 distribución: licencia, metadatos alfa, changelog, CI de cuatro entornos,
   recursos reproducibles y smoke test del wheel instalado fuera del checkout.
4. Ejecutar matriz, builds, auditorías y revisión independiente; corregir
   hallazgos relevantes, integrar en main local y entregar los artefactos.

La publicación remota y la subida a TestPyPI/PyPI son pasos posteriores explícitos.
No se solicitarán credenciales en el chat. CI queda preparada; su ejecución remota
solo podrá acreditarse tras subir el repositorio.

## Registro

- Pre-flight: T15 produce navegación/documentación de limitaciones que consume T16.
  Documentar únicamente comportamiento implementado; no anunciar certificación WCAG.
- Trabajo en la rama codex/alpha-readiness del checkout habitual, preservando demo y stash.

- T15: completo. Auditoría observada RED→GREEN: controles sin nombre accesible y menú móvil oculto.
  Suite principal: 98/98; reflow LTR/RTL y axe claro/oscuro pasan.

- T16: completo localmente. Sphinx/MyST/Furo con guías y búsqueda verificadas;
  workflows con Actions fijadas por SHA y validados por actionlint v1.7.12; licencia
  BSD3, metadatos alfa y avisos de terceros incluidos. Twine 7 requerido para metadata 2.5.
- Final: corregidos los dos P2 de la revisión mediante regresiones RED→GREEN.
  Suite 100/100 en las cuatro combinaciones; ninguna observación aplazada.
- Wheel original y reconstruido desde sdist instalados fuera del checkout;
  pip y smoke con Django 6.0.9/6.1.2 pasan. Sphinx estricto, Ruff y recursos pasan.
- No hay publicación remota ni credenciales configuradas por esta ejecución.
  El checkpoint final de publicación requiere la decisión del usuario y CI remoto.
