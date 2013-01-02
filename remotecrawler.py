#!/usr/bin/env python
# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND ISC DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL ISC BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.

from django.core.management import setup_environ
from socket import gethostname
import socket
import settings
import types
from xml.dom import minidom
import sys, os, ldap, paramiko

setup_environ(settings)

from updates.models import *


ds = ldap.initialize(settings.LDAP_HOST)

puppethosts = ds.search_s(settings.LDAP_BASE,ldap.SCOPE_SUBTREE,'(objectClass=puppetClient)')

client = paramiko.SSHClient()
client.load_host_keys("/etc/ssh/ssh_known_hosts")

for puppethost in puppethosts:
    hostname = puppethost[1]['cn'][0]
    sys.stderr.write("Fetching update info from host %s\n" % hostname)

    try:
        host = Host.objects.filter(hostname=hostname)[0]
    except IndexError:
        host = None

    if not host:
        host = Host(hostname=hostname)
        host.save()

    try:
        client.connect(hostname,key_filename=settings.SSH_KEY_FILE,timeout=3,username=settings.SSH_USER)
    except:
        sys.stderr.write("Failed, trying next host.\n")
        client.close()
        continue

    # Invoke the shell
    # As we are using command restrictions on the server side, this will
    # automatically output our XML feed
    shell = client._transport.open_session()
    shell.invoke_shell()

    # Make a file-like object to feed minidom's parser with
    xmloutput = shell.makefile('rb',-1)
    
    try:
        xml = minidom.parse(xmloutput)
    except:
        sys.stderr.write("Failed to parse xml, trying next host\n")
        client.close()
        continue

    client.close()

    # Clear all previous update entries
    host.update_set.all().delete()

    for update in xml.getElementsByTagName("package"):
        name = update.getAttribute("name")
        cv = update.getAttribute("current_version")
        nv = update.getAttribute("new_version")
        sn = update.getAttribute("source_name")
        is_sec = (update.getAttribute("is_security") == "true")

        try: 
            p = Package.objects.filter(name=name)[0]
        except IndexError:
            p = None
        if not p:
            p = Package(name=name, sourcename=sn)
            p.save()
        u = Update(host=host, package=p,
                installedVersion=cv, candidateVersion=nv,
                is_security=is_sec)
        u.save()

    # Update the host's last-visited timestamp
    host.save()

# Delete orphaned packages from previous runs
Package.objects.filter(hosts__isnull=True).delete()
