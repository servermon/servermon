from virt.models import *

def sync_vms():
    for node in Node.objects.all():
        try:
            vms = node.get_running_vms()
            if not node.reachable:
                node.reachable = True
                node.save()
        except:
            node.reachable = False
            node.save()
            continue

        for vm in vms:
            try:
                domain = Domain.objects.get(name=vm.name())
            except:
                domain = Domain()
                domain.name = vm.name()
                domain.description = vm.name()

            try:
                domain.puppet_host = Host.objects.get(name=vm.name())
            except:
                pass

            domain.node = node
            domain.memory = vm.maxMemory() / 1024
            domain.current_memory = vm.maxMemory() / 1024
            domain.number_of_vcpus = vm.info()[3]
            domain.os_type = vm.OSType()
            domain.xml = vm.XMLDesc(0)
            domain.type = 'xen'
            domain.active = True
            domain.cluster = node.cluster
            domain.save()
