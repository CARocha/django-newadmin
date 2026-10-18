#!/usr/bin/env python
"""Manage the local NewAdmin demo."""

import os
import sys
from pathlib import Path

from django.core.management import execute_from_command_line

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.config.settings")
execute_from_command_line(sys.argv)
