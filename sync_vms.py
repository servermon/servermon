#!/usr/bin/env python
from django.core.management import setup_environ
import settings

setup_environ(settings)

from virt.util import sync_vms

sync_vms()
