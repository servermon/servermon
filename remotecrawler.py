#!/usr/bin/env python
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

        try: 
            p = Package.objects.filter(name=name)[0]
        except IndexError:
            p = None
        if not p:
            p = Package(name=name, sourcename=sn)
            p.save()
        u = Update(host=host, package=p, installedVersion=cv, candidateVersion=nv)
        u.save()

    # Update the host's last-visited timestamp
    host.save()

