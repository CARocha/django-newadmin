"""Public package identity and installation contract for the first alpha."""
from importlib import metadata, resources

from django.apps import AppConfig
from django.template import Template
from django.test import Client


def test_package_configuration_assets_and_templates_share_the_new_identity(settings):
    import newadmin
    from newadmin.conf import get_options

    assert metadata.version('django-newadmin') == newadmin.__version__
    assert AppConfig.create('newadmin').name == 'newadmin'
    settings.NEWADMIN = {'SITE_HEADER': 'NewAdmin studio'}
    assert get_options()['SITE_HEADER'] == 'NewAdmin studio'
    package = resources.files('newadmin')
    assert package.joinpath('static/newadmin/css/newadmin.css').is_file()
    assert package.joinpath('templates/newadmin/dashboard/layout.html').is_file()
    assert Template('{% load newadmin %}').nodelist is not None
    response = Client().get('/admin/login/')
    assert response.status_code == 200
    assert b'NewAdmin studio' in response.content
    assert b'newadmin-theme' in response.content
    assert b'newadmin/css/newadmin.css' in response.content
