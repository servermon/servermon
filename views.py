from puppet.models import Host, Fact, FactValue
from updates.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect
from datetime import datetime, timedelta
from django.db.models import Q
from IPy import IP
import re

def host(request,host):
    host = get_object_or_404(Host, name=host)

    iflist = host.factvalue_set.get(fact_name__name='interfaces').value.split(',')
    interfaces = []
    for iface in iflist:
        iface1 = iface.replace(':','_')
        try:
            mac = host.factvalue_set.get(fact_name__name='macaddress_%s' % iface1).value
        except:
            mac = None
        try:
            ip = host.factvalue_set.get(fact_name__name='ipaddress_%s' % iface1).value
            netmask = host.factvalue_set.get(fact_name__name='netmask_%s' % iface1).value
        except:
            ip = None
            netmask = None

        interfaces.append({
            'iface': iface,
            'mac': mac,
        })

        if netmask and ip:
            interfaces[-1]['ipaddr'] = "%s/%d" % (ip, IP(ip).make_net(netmask).prefixlen())
        
    system = []
    system.append({ 'name': 'BIOS Date',
        'value': host.get_fact_value('bios_date')
        })
    system.append({ 'name': 'BIOS Version',
        'value': host.get_fact_value('bios_version')
        })
    system.append({ 'name': 'System Vendor',
        'value': host.get_fact_value('manufacturer')
        })
    system.append({ 'name': 'Model',
        'value': host.get_fact_value('productname')
        })
    system.append({ 'name': 'Serial Nr',
        'value': host.get_fact_value('serialnumber')
        })
    system.append({ 'name': 'Memory',
        'value': "%s (%s free)" % (host.get_fact_value('memorysize'), host.get_fact_value('memoryfree'))
        })
    system.append({ 'name': 'Processors',
        'value': host.get_fact_value('processorcount')
        })
    system.append({ 'name': 'Processor type',
        'value': ", ".join([ p['value'] for p in host.factvalue_set.filter(fact_name__name__startswith='processor').exclude(fact_name__name='processorcount').values('value').distinct() ]),
	})
    system.append({ 'name': 'Architecture',
        'value': host.get_fact_value('architecture')
        })
    system.append({ 'name': 'Operating System',
        'value': "%s %s" % (host.get_fact_value('operatingsystem'), host.get_fact_value('operatingsystemrelease'))
        })
    system.append({ 'name': 'Machine type',
        'value': host.get_fact_value('virtual')
        })

    system.append({ 'name': 'Puppet classes',
        'value': ", ".join([ f.value for f in  host.factvalue_set.filter(fact_name__name='puppetclass') ])
        })

    #return render_to_response("host.html", { 'host': host, 'interfaces': interfaces, 'system': system })

    updates = host.update_set.order_by('package__name')
    return render_to_response('hostview.html', {'host': host, 'updates': updates, 'interfaces': interfaces, 'system': system })


def inventory(request):
    hosts = Host.objects.filter(factvalue__fact_name__name='system_vendor').order_by('name')

    hostlist = []
    for host in hosts:
        hostlist.append({
            'name': host.name,
            'vendor': host.get_fact_value('system_vendor'),
            'model': host.get_fact_value('system_name'),
            'biosdate': host.get_fact_value('bios_date'),
            'biosversion': host.get_fact_value('bios_version'),
            'serial': host.get_fact_value('serialnumber'),
            'arch': host.get_fact_value('architecture'),
            'cpus': host.get_fact_value('processorcount'),
            })

    return render_to_response("inventory.html", {'hosts': hostlist})

def index(request):
    hosts = Host.objects.all()
    problemhosts = Host.objects.filter(updated_at__lte=(datetime.now() - timedelta(seconds=3600))).order_by('name')
    factcount = Fact.objects.count()
    factvaluecount = FactValue.objects.count()
    updatecount = Host.objects.filter(package__isnull=False).distinct().count()
    packagecount = Package.objects.count()

    return render_to_response("index.html", {
        'problemhosts': problemhosts, 
        'hosts': hosts,
        'factcount': factcount,
        'factvaluecount': factvaluecount,
        'updatecount': updatecount,
        'packagecount': packagecount,
        })

def search(request):
    if not request.POST or (not 'search' in request.POST):
        return HttpResponseRedirect('/')

    
    matches = []
    regex = re.compile(r'(' + request.POST['search'] + ')', re.IGNORECASE)
    for name, field in [('Hostname', 'fqdn'), ('MAC Address', 'macaddress_'), ('IP Address', 'ipaddress_'), ('Vendor', 'system_vendor'), ('Model', 'system_name'), ('Puppet class', 'puppetclass'), ('Operating system', 'operatingsystem')]:
        res = FactValue.objects.filter(fact_name__name__startswith=field, value__icontains=request.POST['search']).distinct().order_by('host__name')
        for r in res:
            matches.append({'name': r.host.name, 'attribute': name, 'value': regex.sub(r'<strong>\1</strong>', r.value)})

    return render_to_response("search.html", {'matches': matches , 'search': request.POST['search'] })
