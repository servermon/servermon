#!/usr/bin/env python
from socket import gethostname
import apt
from xml.dom.minidom import Document

def getUpdates():
    cache = apt.Cache()
    cache.upgrade()

    updates = cache.getChanges()
    doc = Document()

    host = doc.createElement("host")
    host.setAttribute("name",gethostname())

    doc.appendChild(host)

    for update in updates:
        u = doc.createElement("package")
        u.setAttribute("name",update.name)
        u.setAttribute("current_version",update.installedVersion)
        u.setAttribute("new_version",update.candidateVersion)
        host.appendChild(u)

    return doc.toprettyxml()

if __name__ == '__main__':
    print getUpdates()
