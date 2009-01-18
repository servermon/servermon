#!/usr/bin/env python
from django.core.management import setup_environ
from socket import gethostname
import settings
import types
from genxml import getUpdates
from xml.dom import minidom

setup_environ(settings)

from updates.models import *

try:
    host = Host.objects.filter(hostname=gethostname())[0]
except IndexError:
    host = None

if not host:
    host = Host(hostname=gethostname())
    host.save()


xml = minidom.parseString(getUpdates())

host.update_set.all().delete()

for update in xml.getElementsByTagName("package"):
    name = update.getAttribute("name")
    cv = update.getAttribute("current_version")
    nv = update.getAttribute("new_version")

    try: 
        p = Package.objects.filter(name=name)[0]
    except IndexError:
        p = None
    if not p:
        p = Package(name=name)
        p.save()
    u = Update(host=host, package=p, installedVersion=cv, candidateVersion=nv)
    u.save()

