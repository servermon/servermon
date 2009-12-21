import libvirt

from django.db import models
from puppet.models import Host
from django.contrib.auth.models import User
from xml.dom.minidom import parseString
from datetime import datetime, timedelta
from settings import VM_TIMEOUT
import xml.etree.ElementTree as et
import uuid

class Cluster(models.Model):
    """This is a pretty cluster"""
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    location = models.TextField(blank=True)
    #filers = models.ManyToManyField(Filer, through='ClusterFiler', null=True)

    def __unicode__(self):
        return self.name

    def get_running_vms(self):
        domains = []
        for node in self.node_set.all():
            domains.extend(node.get_running_vms())
        return domains

    def get_vm_by_name(self,name):
        for node in self.node_set.all():
            dom = node.get_vm_by_name(name)
            if dom:
                dom.node = node
                return dom
        return None

    def get_capabilities(self):
        caps = filter(lambda cap: reduce(lambda x,y: x | getattr(y, 'has_' + cap), self.node_set.all(), 0) == True, ('xen', 'kvm', 'openvz', 'lxc'))
        return caps

    def capabilities(self):
        return ", ".join(self.get_capabilities())
            

#class ClusterFiler(models.Model):
#    cluster = models.ForeignKey(Cluster)
#    filer = models.ForeignKey(Filer)
#    initiator_group = models.CharField(max_length=64)
#
#    def __unicode__(self):
#        return "Connection of %s to %s as initiator group %s" % (self.cluster.name, self.filer.name, self.initiator_group)

class Node(models.Model):
    TRANSPORTS = (
        ('tls', 'TLS'),
        ('tcp', 'TCP'),
        ('ssh', 'SSH')
    )

    host = models.ForeignKey(Host, limit_choices_to={ 'factvalue__fact_name__name': 'system_vendor' })
    cluster = models.ForeignKey(Cluster,blank=True,null=True)
    notes = models.TextField(blank=True)
    transport = models.CharField(max_length=20,choices=TRANSPORTS, default='tcp')
    reachable = models.BooleanField(default=False)

    @property
    def hostname(self):
        return self.host.name

    class Meta:
        ordering = ['host__name']

    def __unicode__(self):
        return self.hostname

    def nodename(self):
        return self.hostname.split('.')[0]

    def get_running_vms(self):
        domains = []
        for uri in self.get_uris():
            hypervisor = libvirt.openReadOnly(uri)
            domains.extend(map(lambda x: hypervisor.lookupByID(x), hypervisor.listDomainsID()))
        for domain in domains:
            domain.node = self
        return filter(lambda x: x.ID() != 0, domains)

    def get_info(self):
        hypervisor = libvirt.openReadOnly('remote+' + self.transport + '://' + self.hostname + '/')
        return hypervisor.getInfo()

    def get_free_memory(self):
        hypervisor = libvirt.openReadOnly('remote+' + self.transport + '://' + self.hostname + '/')
        return hypervisor.getFreeMemory()

    def get_vm_by_name(self,name):
        for uri in self.get_uris():
            hypervisor = libvirt.openReadOnly(uri)
            try:
                return hypervisor.lookupByName(name)
            except:
                return None

    def get_uris(self):
        hypervisors = sorted(set([ x['hypervisor'] for x in self.get_capabilities()]))
        return [ h + '+' + self.transport + '://' + self.hostname + '/' for h in hypervisors]

    def get_capabilities(self):
        caps = [] 
        conn = libvirt.openReadOnly('remote+' + self.transport + '://' + self.hostname + '/')
        try:
            xml = parseString(conn.getCapabilities())
        except:
            return []
        for guest in xml.getElementsByTagName('guest'):
            for domtype in guest.getElementsByTagName('arch')[0].getElementsByTagName('domain'):
                caps.append({
                'type': guest.getElementsByTagName('os_type')[0].childNodes[0].nodeValue,
                'arch': guest.getElementsByTagName('arch')[0].getAttribute('name'),
                'hypervisor': domtype.getAttribute('type')
            })
        return caps

    # Helpers for the admin interface list
    def has_xen(self):
        if filter(lambda x: x['hypervisor'] == 'xen', self.get_capabilities()):
            return True
        return False
    has_xen.boolean = True

    def has_qemu(self):
        if filter(lambda x: x['hypervisor'] == 'qemu', self.get_capabilities()):
            return True
        return False
    has_qemu.boolean = True

    def has_kvm(self):
        if filter(lambda x: x['hypervisor'] == 'kvm', self.get_capabilities()):
            return True
        return False
    has_kvm.boolean = True
        
    def has_openvz(self):
        if filter(lambda x: x['hypervisor'] == 'openvz', self.get_capabilities()):
            return True
        return False
    has_openvz.boolean = True

    def get_host_arch(self):
        conn = libvirt.openReadOnly('remote+' + self.transport + '://' + self.hostname + '/')
        try:
            xml = parseString(conn.getCapabilities())
        except:
            return "N/A"
        return xml.getElementsByTagName('host')[0].getElementsByTagName('arch')[0].childNodes[0].nodeValue
    get_host_arch.short_description = 'Host architecture'

    def status(self):
        #try:
        #    conn = libvirt.openReadOnly('remote+' + self.transport + '://' + self.hostname + '/')
        #    return True
        #except:
        #    return False
        return self.reachable
    status.boolean = True
        

class VLAN(models.Model):
    vlan_id = models.IntegerField()
    description = models.CharField(max_length=100)
    cluster = models.ForeignKey(Cluster)

    def __unicode__(self):
        return "VLAN #%d (%s)" % (self.vlan_id, self.description)


class Domain(models.Model):
    DOM_TYPES = ( ('kvm', 'KVM'), ('xen', 'Xen'), ('openvz', 'OpenVZ'), ('qemu','Qemu'), ('lxc', 'LXC'), ('kqemu', 'kqemu') )
    OS_TYPES = ( ('hvm', 'Fully Virtualized'), ('linux', 'Xen PV' ), ('qemu','KVM PV') )
    BOOT_TYPES = ( ('a', 'floppy'), ('c', 'hdd'), ('d', 'cdrom'), ('n', 'network'), ('ac', 'floppy,hdd'), ('ad', 'floppy,cdrom'), ('an', 'floppy,network'), ('cd', 'hdd,cdrom'), ('cn', 'hdd,network'), ('dc', 'cdrom,hdd'), ('dn', 'cdrom,network'), )
    LIFECYCLE_TYPES = ( ('destroy','destroy'), ('restart','restart'), ('preserve','preserve'), ('rename-restart','rename-restart') )
    CLOCK_TYPES	= ( ('localtime','Local time'), ('utc','UTC') )

    type = models.CharField(max_length=20, choices=DOM_TYPES, default='kvm')
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    notes = models.TextField()
    uuid = models.CharField(max_length=50, editable=False)
    approved = models.BooleanField(default=False)
    active = models.BooleanField(default=False)
    autostart = models.BooleanField(default=False)
    owners = models.ManyToManyField(User)
    cluster = models.ForeignKey(Cluster, null=True, blank=True)
    node = models.ForeignKey(Node)
    puppet_host = models.ForeignKey(Host, null=True, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    xml = models.TextField(blank=True)
    #luns = models.ManyToManyField(Filer, through='DomainLUN', blank=True)
    #vlans = models.ManyToManyField(VLAN, blank=True)

    memory = models.PositiveIntegerField(default=512)
    current_memory = models.PositiveIntegerField(null=True, blank=True)
    number_of_vcpus = models.PositiveIntegerField(default=1)

    """ Bootloader configuration details """
    bootloader = models.CharField(max_length=100, null=True, blank=True)
    bootloader_args = models.CharField(max_length=200, null=True, blank=True)

    """ OS configuration details """
    os_type = models.CharField(max_length=6, choices=OS_TYPES)
    loader = models.CharField(max_length=100, null=True, blank=True)
    os_arch = models.CharField(max_length=10, null=True, blank=True)
    os_machine = models.CharField(max_length=10, null=True, blank=True)
    os_kernel = models.CharField(max_length=200, null=True, blank=True)
    os_initrd = models.CharField(max_length=200, null=True, blank=True)
    os_cmdline = models.CharField(max_length=200, null=True, blank=True)
    os_boot = models.CharField(max_length=4, choices=BOOT_TYPES, null=True, blank=True, default='c')

    """ Lifecycle behavior """
    poweroff = models.CharField(max_length=14, choices=LIFECYCLE_TYPES, null=True, blank=True, default='destroy')
    reboot = models.CharField(max_length=14, choices=LIFECYCLE_TYPES, null=True, blank=True)
    crash = models.CharField(max_length=14, choices=LIFECYCLE_TYPES, null=True, blank=True)

    """ Hypervisor features """
    pae = models.BooleanField(default=False)
    acpi = models.BooleanField(default=False)
    apic = models.BooleanField(default=False)

    """ Clock settings """
    clock = models.CharField(max_length=9, choices=CLOCK_TYPES, null=True, blank=True)

    #""" Template (if any) from which the VM was created """
    #template = models.ForeignKey(DomainTemplate, null=True, blank=True, editable=False)

    @property 
    def puppetized(self):
        if self.puppet_host:
            return True
        return False

    def is_alive(self):
        if datetime.now() - self.last_seen < timedelta(seconds=VM_TIMEOUT):
            return True
        return False

    def is_puppetized(self):
        return self.puppetized
    is_puppetized.boolean = True

    def get_contacts(self):
        return ", ".join([ c.name for c in self.domaincontact_set.all() ])
    get_contacts.short_description = 'contacts'

    """ Generation of XML to adhere to libvirt domain format """
    def pretty_xml(self):
        self.get_xml()
        xml = self.xml
        return xml.toprettyxml()
    
    def get_xml(self):
    	xml = Document()
    
    	domain = xml.createElement("domain")
        domain.setAttribute("type", self.type)
        
        if self.id:
    	   domain.setAttribute("id", str(self.id) )
    
        xml.appendChild(domain)
    
        name = xml.createElement("name")
        domain.appendChild(name)
        name_text = xml.createTextNode(self.name)
        name.appendChild(name_text)
    
        uuid = xml.createElement("uuid")
        domain.appendChild(uuid)
        uuid_text = xml.createTextNode(self.uuid)
        uuid.appendChild(uuid_text)
    
        """ Create bootloader and bootloader_args tags """
        if self.bootloader:
    	    bootloader = xml.createElement("bootloader")
    	    domain.appendChild(bootloader)
    	    bootloader_path = xml.createTextNode(self.bootloader)
    	    bootloader.appendChild(bootloader_path)
    	    if self.bootloader_args:
    		bootloader_args = xml.createElement("bootloader_args")
    		domain.appendChild(bootloader_args)
    		bootloader_args_text = xml.createTextNode(self.bootloader_args)
    		bootloader_args.appendChild(bootloader_args_text)
    
    
        """ Create OS element tags """
        os = xml.createElement("os")
        domain.appendChild(os)
    
        os_type = xml.createElement("type")
        os.appendChild(os_type)
        os_dom_type = xml.createTextNode(self.os_type)
        os_type.appendChild(os_dom_type)
        
        if self.os_arch:
            os_type.setAttribute("arch", self.os_arch)
        
        if self.os_machine:
            os_type.setAttribute("machine", self.os_machine)
        
            if self.loader:
                os_loader = xml.createElement("loader")
                os.appendChild(os_loader)
                os_loader_text = xml.createTextNode(self.loader)
                os_loader.appendChild(os_loader_text)
        
        if self.os_kernel:
            os_kernel = xml.createElement("kernel")
            os.appendChild(os_kernel)
            os_kernel_text = xml.createTextNode(self.os_kernel)
            os_kernel.appendChild(os_kernel_text)
        
        if self.os_initrd:
            os_initrd = xml.createElement("initrd")
            os.appendChild(os_initrd)
            os_initrd_text = xml.createTextNode(self.os_initrd)
            os_initrd.appendChild(os_initrd_text)
        
        if self.os_cmdline:
                os_cmdline = xml.createElement("cmdline")
                os.appendChild(os_cmdline)
                os_cmdline_text = xml.createTextNode(self.os_cmdline)
                os_cmdline.appendChild(os_cmdline_text)
        
        if self.os_boot:
            boot_device_list = str(self.os_boot)
            for boot_dev_count in range(0, len(boot_device_list)):
            	boot_dev_char = boot_device_list[boot_dev_count]
            	if boot_dev_char == "a":
            	   boot_dev = "fd"
            	if boot_dev_char == "c":
            	   boot_dev = "hd"
            	if boot_dev_char == "d":
            	   boot_dev = "cdrom"
            	if boot_dev_char == "n":
            	   boot_dev = "network"
            
            	os_boot = xml.createElement("boot")
            	os.appendChild(os_boot)
            	os_boot.setAttribute("dev", boot_dev)
        
        memory = xml.createElement("memory")	
        domain.appendChild(memory)
        memory_text = xml.createTextNode( str(self.memory) )
        memory.appendChild(memory_text)
        
        if self.current_memory:
                current_memory = xml.createElement("current_memory")   
                domain.appendChild(current_memory)
                current_memory_text = xml.createTextNode( str(self.current_memory) )
                current_memory.appendChild(current_memory_text)
        
        vcpu = xml.createElement("vcpu")   
        domain.appendChild(vcpu)
        vcpu_text = xml.createTextNode( str(self.number_of_vcpus) )
        vcpu.appendChild(vcpu_text)
    
        if self.poweroff:
            on_poweroff = xml.createElement("on_poweroff")
            domain.appendChild(on_poweroff)
            on_poweroff_text = xml.createTextNode(self.poweroff)
            on_poweroff.appendChild(on_poweroff_text)
        
        if self.reboot:
                on_reboot = xml.createElement("on_reboot")
                domain.appendChild(on_reboot)
                on_reboot_text = xml.createTextNode(self.reboot)
                on_reboot.appendChild(on_reboot_text)
        
        if self.crash:
                on_crash = xml.createElement("on_crash")
                domain.appendChild(on_crash)
                on_crash_text = xml.createTextNode(self.crash)
                on_crash.appendChild(on_crash_text)
        
        if self.pae or self.acpi or self.apic:
            features = xml.createElement("features")
            domain.appendChild(features)
        
        if self.pae:
            pae = xml.createElement("pae")
            features.appendChild(pae)
        
            if self.acpi:
                acpi = xml.createElement("acpi")
                features.appendChild(acpi)
        
            if self.apic:
                apic = xml.createElement("apic")
                features.appendChild(apic)
        
        if self.clock:
            clock = xml.createElement("clock")
            clock.setAttribute("sync", self.clock)
            domain.appendChild(clock)
           
        
        """ Domain Devices """
        devices = xml.createElement("devices")
        domain.appendChild(devices)
        
        """ Ready disk images """
        for image in self.image_set.all():
            domimg = image.domainimage_set.get(domain=self)
            disk = xml.createElement('disk')
            devices.appendChild(disk)
            disk.setAttribute('type', 'file')
            if domimg.device:
                disk.setAttribute('device', domimg.device)
            
            source = xml.createElement('source')
            disk.appendChild(source)
            source.setAttribute('file', pathjoin(image.pool.path, image.filename))
            target = xml.createElement("target")
            disk.appendChild(target)
            target.setAttribute("dev", domimg.target)

        """ LUNs """
        for lun in self.domainlun_set.all():
            disk = xml.createElement('disk')
            devices.appendChild(disk)
            disk.setAttribute('type', 'block')
            
            source = xml.createElement('source')
            disk.appendChild(source)
            source.setAttribute('dev', '/dev/disk/netapp/' + lun.get_serial() )
            target = xml.createElement("target")
            disk.appendChild(target)
            target.setAttribute("dev", domimg.target)

        """ Domain disk devices """
        for disk_device in self.disk_set.all():
            disk = xml.createElement("disk")
            devices.appendChild(disk)
            disk.setAttribute("type", disk_device.disk_type)
            if disk_device.device:
                disk.setAttribute("device", disk_device.device)
        
            source = xml.createElement("source")
            disk.appendChild(source)
        
            if disk_device.disk_type == "file":
        	   disk_location = "file"
            else:
        	   disk_location = "dev"
        
            source.setAttribute(disk_location, disk_device.source)
        
            target = xml.createElement("target")
            disk.appendChild(target)
            target.setAttribute("dev", disk_device.target)
            if disk_device.bus:
        	   target.setAttribute("bus", disk_device.bus)
        
            if disk_device.driver_name and disk_device.driver_type:
                driver = xml.createElement("driver")
                disk.appendChild(driver)
                
                driver.setAttribute("name",self.driver_name)
                driver.setAttribute("type",self.driver_type)
        
            if disk_device.readonly:
        	   readonly = xml.createElement("readonly")
        	   disk.appendChild(readonly)
        
        """ Domain interface devices """
        for interface_device in self.interface_set.all():
            interface = xml.createElement("interface")
            devices.appendChild(interface)
            interface.setAttribute("type", interface_device.interface_type)
                
            if interface_device.interface_type in ('network', 'bridge', 'mcast'):
        	   source = xml.createElement("source")
        	   interface.appendChild(source)
        	   if interface_device.source_name:
        	       source.setAttribute(interface_device.interface_type, interface_device.source_name)
        
            if interface_device.target_device:
                target = xml.createElement("target")
                interface.appendChild(target)
                target.setAttribute("dev", interface_device.target_device)
                
            if interface_device.interface_model:
                model = xml.createElement("model")
                interface.appendChild(model)
                model.setAttribute("type", interface_device.interface_model)
            
            if interface_device.mac_address:
                mac = xml.createElement("mac")
                interface.appendChild(mac)
                mac.setAttribute("address", interface_device.mac_address)

            if interface_device.script_path:
                script = xml.createElement("script")
                interface.appendChild(script)
                script.setAttribute("path", interface_device.script_path)
        
        """ Domain graphics devices """
        for graphics_device in self.graphics_set.all():
            graphics = xml.createElement("graphics")
            devices.appendChild(graphics)
    
            if graphics_device.type == "sdl":
                if graphics_device.sdl_display:
                        graphics.setAttribute("display", raphics_device.sdl_display)
                    
                if graphics_device.sdl_xauth:
                        graphics.setAttribute("xauth",graphics_device.sdl_xauth)
                    
                if graphics_device.sdl_fullscreen:
                        graphics.setAttribute("fullscreen", "yes")
                
            else:
                if graphics_device.vnc_port:
                        graphics.setAttribute("port", str(graphics_device.vnc_port) )
            
                if graphics_device.vnc_listen:
                        graphics.setAttribute("listen",graphics_device.vnc_listen)
            
            graphics.setAttribute("type", graphics_device.type)
        
        self.xml = xml
        self.save()
        
        return xml.toxml()


    def save(self, force_insert=False, force_update=False):
        if not self.uuid:
            self.uuid = str(uuid.uuid4())
        super(Domain, self).save(force_insert, force_update)

    def get_disks(self):
        tree = et.fromstring(self.xml)
        disks = []
        for disk in tree.findall('devices/disk'):
            d = {}
            d['type'] = disk.get('type')
            d['device'] = disk.get('device')
            try:
                d['source'] = disk.find('source').get('dev')
            except:
                pass
            try:
                d['target'] = disk.find('target').get('dev')
            except:
                pass
            disks.append(d)
        return disks

    def get_interfaces(self):
        tree = et.fromstring(self.xml)
        ifaces = []
        for iface in tree.findall('devices/interface'):
            i = {}
            i['type'] = iface.get('type')
            i['mac'] = iface.find('mac').get('address')
            if i['type'] == 'bridge':
                i['bridge'] = iface.find('source').get('bridge')
                i['name'] = iface.find('target').get('dev')
            ifaces.append(i)
        return ifaces

    class Meta:
        ordering = 'name',

    def __unicode__(self):
        return self.name

class DomainContact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    domains = models.ManyToManyField(Domain)

    def __unicode__(self):
        return "%s (%s)" % (self.name, self.email)
