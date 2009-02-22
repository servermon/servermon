from xml.dom.minidom import parseString
from updates.models import Package, Update

def clean_orphan_packages():
    Package.objects.filter(hosts__isnull=True).delete()

def gen_host_updates(host):
    # Delete old updates
    host.update_set.all().delete()

    try:
        xml = parseString(host.get_fact_value('package_updates'))
    except:
        return

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
