# Desarrollo y publicación de la alfa

## Construir la documentación

```sh
python -m pip install -e '.[dev,docs]'
python -m sphinx -n -W --keep-going -b html docs docs/_build/html
python -m http.server 8002 --directory docs/_build/html
```

Sphinx usa MyST para las guías Markdown existentes y Furo para la presentación.
No hace falta un servidor Django para consultar el HTML generado. La configuración
`.readthedocs.yaml` permite importarlo en Read the Docs; conectar/publicar ese
proyecto es una acción del mantenedor que todavía no se ha realizado.

## Publicar la documentación en GitHub Pages

El workflow `.github/workflows/docs.yml` construye el HTML con Sphinx y lo
despliega automáticamente al hacer push a `main` cuando cambian los archivos de
`docs/` o `pyproject.toml`. Para habilitar el destino una vez, abre
[Settings → Pages](https://github.com/CARocha/django-newadmin/settings/pages)
del repositorio y selecciona **GitHub Actions** como *Build and deployment →
Source*. Luego de guardar, el workflow publica el sitio en
<https://carocha.github.io/django-newadmin/>. También se puede ejecutar desde
Actions → **Documentation** → Run workflow.

## Verificación del candidato

```sh
npm ci
npm run build:css
npm run build:icons
npm run build:charts
npm run test:js
python -m playwright install chromium
python -m pytest -q
python -m ruff check .
python demo/manage.py check
python demo/manage.py makemigrations --check --dry-run
python -m sphinx -n -W --keep-going -b html docs docs/_build/html
python -m build
python -m twine check --strict dist/django_newadmin-0.1.0a1*
```

CI repite las cuatro combinaciones Python/Django, reconstruye los recursos para
comprobar que están al día y genera el sitio Sphinx y las distribuciones como
artefactos. Un segundo entorno instala el wheel fuera del checkout y ejecuta
`scripts/smoke_wheel.py`: importación instalada, login, portada, formulario,
plantillas y staticfiles con manifiesto. No se publica automáticamente.

Para repetir la instalación limpia local, crea un entorno separado, instala el
wheel (sin `-e`) y ejecuta el script con su intérprete:

```sh
python -m venv /tmp/newadmin-wheel-test
/tmp/newadmin-wheel-test/bin/python -m pip install dist/django_newadmin-0.1.0a1-py3-none-any.whl
/tmp/newadmin-wheel-test/bin/python scripts/smoke_wheel.py
```

El script rechaza una importación desde el checkout para evitar un falso positivo.

## Conectar TestPyPI y PyPI con GitHub Actions

Los workflows ya están preparados para Trusted Publishing: no guardan tokens
de PyPI en GitHub. En TestPyPI y PyPI hay que registrar el repositorio y el
workflow que cada servicio aceptará. En ambas cuentas, activa 2FA.

En [TestPyPI](https://test.pypi.org), inicia sesión, abre Account settings →
Publishing y registra un **pending publisher** con estos valores:

| Campo | Valor |
| --- | --- |
| PyPI project name | `django-newadmin` |
| Owner | `CARocha` |
| Repository name | `django-newadmin` |
| Workflow name | `publish-testpypi.yml` |
| Environment name | `testpypi` |

Después, en GitHub abre Actions → **Publish to TestPyPI** → Run workflow y
ejecútalo desde `main`. El workflow compila y verifica las distribuciones antes
de subirlas. La primera publicación crea el proyecto en TestPyPI; un pending
publisher no reserva el nombre hasta que se usa.

Comprueba la instalación desde TestPyPI en un entorno temporal, con Django
instalado desde PyPI:

```sh
python -m venv /tmp/probar-newadmin
/tmp/probar-newadmin/bin/python -m pip install 'Django>=6.0,<6.2'
/tmp/probar-newadmin/bin/python -m pip install \
  --index-url https://test.pypi.org/simple/ --no-deps django-newadmin
```

En [PyPI](https://pypi.org), inicia sesión y registra otro pending publisher
desde Account settings → Publishing:

| Campo | Valor |
| --- | --- |
| PyPI project name | `django-newadmin` |
| Owner | `CARocha` |
| Repository name | `django-newadmin` |
| Workflow name | `publish-pypi.yml` |
| Environment name | `pypi` |

Una vez que TestPyPI esté probado, crea en GitHub un Release asociado al tag de
la versión, por ejemplo `v0.1.0a1`. Publicar ese Release dispara el workflow de
PyPI. Confirma que el tag apunta al commit de la versión que aprobaste y que CI
pasó antes de publicarlo. PyPI no permite volver a subir una versión existente.

La primera alfa requiere registrar `0.1.0a1` en ambos índices. La subida a
TestPyPI y la de PyPI son acciones separadas; publicar en uno no publica en el
otro.

## Preparación local de distribuciones

También puedes construir manualmente con Twine si necesitas depurar una
publicación. El flujo normal usa Trusted Publishing:

El candidato usa `0.1.0a1`. Habilita 2FA en ambas cuentas y confirma que CI pasó.
Si usas carga manual, las cuentas y tokens de cada índice son independientes.

```sh
python -m twine upload --repository testpypi dist/django_newadmin-0.1.0a1-py3-none-any.whl dist/django_newadmin-0.1.0a1.tar.gz
```

Prueba ese artefacto con Django previamente instalado desde PyPI, evitando resolver
sus dependencias desde TestPyPI:

```sh
python -m pip install 'Django>=6.0,<6.2'
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps 'django-newadmin==0.1.0a1'
```

Después de verificarlo, la carga manual de **los mismos archivos** a PyPI sería:

```sh
python -m twine upload dist/django_newadmin-0.1.0a1-py3-none-any.whl dist/django_newadmin-0.1.0a1.tar.gz
```

Registra la publicación en el changelog y crea el tag `v0.1.0a1` en el commit
verificado. No reutilices una versión subida: una corrección posterior debe
incrementar la versión alfa. Conserva los hashes SHA-256 de los artefactos.

Si hay un fallo, documenta su alcance y publica una nueva alfa corregida. Un
usuario puede fijar una versión anterior o desactivar `newadmin`; el tema no tiene
migraciones propias. La primera alfa todavía no tiene una versión previa.

Referencias: [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html),
[empaquetado y TestPyPI](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/),
[crear proyecto con Trusted Publisher](https://docs.pypi.org/trusted-publishers/creating-a-project-through-oidc/),
[GitHub Pages con workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).
