#!/usr/bin/env python
from django.core.management import setup_environ
from socket import gethostname
import settings
import apt

setup_environ(settings)

from updates.models import *

host = Host.objects.filter(hostname=gethostname())
if not Host:
    host = Host(hostname=gethostname())
    host.save()
else:
    host = host[0]
cache = apt.Cache()
cache.upgrade()

updates = cache.getChanges()

for update in updates:
    try: 
        p = Package.objects.filter(name=update.name)[0]
    except IndexError:
        p = None
    if not p:
        p = Package(name=update.name)
        p.save()
    u = Update(host=host, package=p, installedVersion=update.installedVersion, candidateVersion=update.candidateVersion)
    u.save()

