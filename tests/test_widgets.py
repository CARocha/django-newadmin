import pytest
from django.contrib.admin.widgets import AdminDateWidget
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from demo.catalog.models import Article


class MediaProbeDateWidget(AdminDateWidget):
    class Media:
        css = {"all": ["adminwp-test/css/widget-probe.css"]}
        js = ["adminwp-test/js/widget-probe.js"]


def test_admin_date_widget_keeps_native_and_custom_media():
    widget = MediaProbeDateWidget()

    assert set(widget.media._js) == {
        "admin/js/calendar.js",
        "admin/js/admin/DateTimeShortcuts.js",
        "adminwp-test/js/widget-probe.js",
    }
    assert widget.media._css["all"] == ["adminwp-test/css/widget-probe.css"]


@pytest.mark.parametrize(
    ("name", "content"),
    [
        ("script.html", b"<script>alert(1)</script>"),
        ("oversized.txt", b"x" * (5 * 1024 * 1024 + 1)),
    ],
    ids=["disallowed-extension", "file-too-large"],
)
def test_demo_attachment_rejects_unapproved_file_uploads(name, content):
    attachment = Article._meta.get_field("attachment")
    uploaded_file = SimpleUploadedFile(name, content)

    with pytest.raises(ValidationError):
        attachment.clean(uploaded_file, None)
