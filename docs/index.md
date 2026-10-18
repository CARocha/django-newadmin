# django-adminwp

Un tema para el administrador de Django, con Bootstrap, apariencia clara/oscura,
navegación inspirada en WordPress y dashboards extensibles con Apache ECharts.

La versión **0.1.0a1** es una alfa: úsala primero en un entorno de pruebas. Su API
puede cambiar entre versiones alfa. El tema conserva el admin y sus permisos;
no necesita modelos, migraciones ni un AdminSite especial.

```{toctree}
:maxdepth: 2
:caption: Guías

installation
configuration
dashboard
extensions
accessibility
troubleshooting
releasing
changelog
```

## Compatibilidad

Python 3.13 y 3.14, con Django 6.0 y 6.1. Los cuatro entornos tienen pruebas
locales; el workflow de CI repite esta matriz cuando se sube el código a GitHub.
Versiones posteriores de Django requieren una nueva verificación.

Bootstrap, iconos y ECharts se distribuyen localmente. Los usuarios del paquete
no necesitan Node, Sass ni servicios externos de gráficos. La licencia del tema
es BSD de 3 cláusulas; cada biblioteca conserva sus propios avisos de licencia.
