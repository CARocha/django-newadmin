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
python -m twine check --strict dist/django_adminwp-0.1.0a1*
```

CI repite las cuatro combinaciones Python/Django, reconstruye los recursos para
comprobar que están al día y genera el sitio Sphinx y las distribuciones como
artefactos. Un segundo entorno instala el wheel fuera del checkout y ejecuta
`scripts/smoke_wheel.py`: importación instalada, login, portada, formulario,
plantillas y staticfiles con manifiesto. No se publica automáticamente.

Para repetir la instalación limpia local, crea un entorno separado, instala el
wheel (sin `-e`) y ejecuta el script con su intérprete:

```sh
python -m venv /tmp/adminwp-wheel-test
/tmp/adminwp-wheel-test/bin/python -m pip install dist/django_adminwp-0.1.0a1-py3-none-any.whl
/tmp/adminwp-wheel-test/bin/python scripts/smoke_wheel.py
```

El script rechaza una importación desde el checkout para evitar un falso positivo.

## Subida a TestPyPI y después PyPI

El candidato usa `0.1.0a1`. Antes de subirlo confirma disponibilidad del nombre,
acceso a las cuentas y el resultado de CI remoto. Las dos plataformas tienen
cuentas/tokens independientes. Configura 2FA y usa un token o Trusted Publishing;
no pegues credenciales en issues, commits o el chat.

Tras la autorización explícita del mantenedor:

```sh
python -m twine upload --repository testpypi dist/django_adminwp-0.1.0a1-py3-none-any.whl dist/django_adminwp-0.1.0a1.tar.gz
```

Prueba ese artefacto con Django previamente instalado desde PyPI, evitando resolver
sus dependencias desde TestPyPI:

```sh
python -m pip install 'Django>=6.0,<6.2'
python -m pip install --index-url https://test.pypi.org/simple/ --no-deps 'django-adminwp==0.1.0a1'
```

Después de verificarlo, sube **los mismos archivos** a PyPI:

```sh
python -m twine upload dist/django_adminwp-0.1.0a1-py3-none-any.whl dist/django_adminwp-0.1.0a1.tar.gz
```

Registra la publicación en el changelog y crea el tag `v0.1.0a1` en el commit
verificado. No reutilices una versión subida: una corrección posterior debe
incrementar la versión alfa. Conserva los hashes SHA-256 de los artefactos.

Si hay un fallo, documenta su alcance y publica una nueva alfa corregida. Un
usuario puede fijar una versión anterior o desactivar `adminwp`; el tema no tiene
migraciones propias. La primera alfa todavía no tiene una versión previa.

Referencias: [Sphinx](https://www.sphinx-doc.org/en/master/usage/quickstart.html),
[empaquetado y TestPyPI](https://packaging.python.org/en/latest/tutorials/packaging-projects/),
[Trusted Publishing](https://docs.pypi.org/trusted-publishers/).
