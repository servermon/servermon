#!/usr/bin/env python
from django.core.management import setup_environ
import settings

setup_environ(settings)

from util import *
from puppet.models import Host

for host in Host.objects.all():
    gen_host_updates(host)

clean_orphan_packages()
