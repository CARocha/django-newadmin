import pytest
from django.core.management import call_command


@pytest.fixture
def static_files(settings, tmp_path):
    settings.STATIC_ROOT = tmp_path / "static"
    call_command("collectstatic", interactive=False, verbosity=0)


@pytest.fixture
def static_live_server(static_files, live_server):
    return live_server
