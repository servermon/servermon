from puppet.models import Host, Fact, FactValue
from virt.models import Domain, Cluster, Node
from updates.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from settings import VM_TIMEOUT, HOST_TIMEOUT
from IPy import IP
import re

def host(request,hostname):
    host = None
    isvm = False
    ispuppet = False
    vmdisks = []
    vmifaces = []
    updates = []
    vms = []
    system = []
    contacts = []
    node = None
    # First try and see if this is a puppet host
    try:
        host = Host.objects.get(name=hostname)
        ispuppet = True
    except:
        pass

    if host:
        for vm in host.domain_set.all():
            isvm = True
            vmdisks = vm.get_disks()
            vmifaces = vm.get_interfaces()
            break
        
    
    else:
        try:
            host = Domain.objects.get(puppet_host__isnull=True, name=hostname)
            vmdisks = host.get_disks()
            vmifaces = host.get_interfaces()
            isvm = True
        except:
            raise Http404


    if ispuppet:
        iflist = host.factvalue_set.get(fact_name__name='interfaces').value.split(',')
        interfaces = []
        for iface in iflist:
            d = {}
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

            d = { 'iface': iface,
                  'mac': mac }

            for vmif in filter(lambda x: x['mac'] == d['mac'], vmifaces):
                try:
                    d['bridge'] = vmif['bridge']
                    d['hostif'] = vmif['name']
                except:
                    pass
                break

            interfaces.append(d)

            if netmask and ip:
                interfaces[-1]['ipaddr'] = "%s/%d" % (ip, IP(ip).make_net(netmask).prefixlen())
            
        system = []
        for fact, label in [
            ('bios_date', 'BIOS Date'),  ('bios_version', 'BIOS Version'),
            ('manufacturer', 'System Vendor'), ('productname', 'Model'),
            ('serialnumber', 'Serial Nr'), ('processorcount', 'Processors'),
            ('architecture', 'Architecture'), ('virtual', 'Machine Type')]:
            system.append({ 'name': label, 'value': host.get_fact_value(fact) })

        system.append({ 'name': 'Processor type',
            'value': ", ".join([ p['value'] for p in host.factvalue_set.filter(fact_name__name__startswith='processor').exclude(fact_name__name='processorcount').values('value').distinct() ]),
        })

        system.append({ 'name': 'Operating System',
            'value': "%s %s" % (host.get_fact_value('operatingsystem'), host.get_fact_value('operatingsystemrelease'))
            })
        system.append({ 'name': 'Memory',
            'value': "%s (%s free)" % (host.get_fact_value('memorysize'), host.get_fact_value('memoryfree'))
            })

        system.append({ 'name': 'Puppet classes',
            'value': ", ".join([ f.value for f in  host.factvalue_set.filter(fact_name__name='puppetclass') ])
            })

        #return render_to_response("host.html", { 'host': host, 'interfaces': interfaces, 'system': system })

        updates = host.update_set.order_by('package__name')

        if host.node_set.all():
            node = host.node_set.all()[0]
            vms =  Domain.objects.filter(node=node)
            for vm in vms:
                contacts.extend([ { 'contact': c, 'vm': vm } for c in vm.domaincontact_set.all() ])
            contacts.sort(cmp=lambda x,y: cmp(x['contact'].name, y['contact'].name))

    else:
        interfaces = vmifaces

    return render_to_response('hostview.html', {'host': host, 'updates': updates, 'interfaces': interfaces, 'system': system, 'vms': vms, 'contacts': contacts, 'node': node, 'vmdisks': vmdisks, 'isvm': isvm, 'ispuppet': ispuppet })


def inventory(request):
    hosts = Host.objects.filter(factvalue__fact_name__name='system_vendor').exclude(factvalue__value='Bochs').order_by('name')

    hostlist = []
    for host in hosts:
        hostlist.append({
            'name': host.name,
            'vendor': host.get_fact_value('system_vendor'),
            'model': host.get_fact_value('system_name'),
            'biosdate': host.get_fact_value('bios_date'),
            'biosversion': host.get_fact_value('bios_version'),
            'serial': host.get_fact_value('serialnumber'),
            'board_serial': host.get_fact_value('board_serial_number', ""),
            'arch': host.get_fact_value('architecture'),
            'cpus': host.get_fact_value('processorcount'),
            })

    return render_to_response("inventory.html", {'hosts': hostlist})

def index(request):
    hosts = Host.objects.all()
    problemhosts = Host.objects.filter(updated_at__lte=(datetime.now() - timedelta(seconds=HOST_TIMEOUT))).order_by('name')
    factcount = Fact.objects.count()
    factvaluecount = FactValue.objects.count()
    updatecount = Host.objects.filter(package__isnull=False).distinct().count()
    packagecount = Package.objects.count()
    problemvms = Domain.objects.filter(last_seen__lte=(datetime.now() - timedelta(seconds=VM_TIMEOUT))).order_by('name')
    vmcount = Domain.objects.count()
    clustercount = Cluster.objects.count()
    nodecount = Node.objects.count()

    return render_to_response("index.html", {
        'problemhosts': problemhosts, 
        'problemvms': problemvms,
        'hosts': hosts,
        'factcount': factcount,
        'factvaluecount': factvaluecount,
        'updatecount': updatecount,
        'packagecount': packagecount,
        'vmcount': vmcount,
        'clustercount': clustercount,
        'nodecount': nodecount,
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

    vms = Domain.objects.filter(name__icontains=request.POST['search'])

    return render_to_response("search.html", {'matches': matches , 'search': request.POST['search'], 'vms': vms })


def query(request):
    class MatrixForm(forms.Form):
        hosts = forms.ModelMultipleChoiceField(queryset=Host.objects.all(), widget=FilteredSelectMultiple("hosts", is_stacked=False))
        facts = forms.ModelMultipleChoiceField(queryset=Fact.objects.exclude(name__startswith='macaddress').exclude(name__startswith='ipaddress').exclude(name__startswith='netmask'), widget=FilteredSelectMultiple("parameters", is_stacked=False))

    if request.method == 'GET':
        f = MatrixForm(label_suffix='')

        return render_to_response("query.html", { 'form': f })

    else:
        f = MatrixForm(request.POST)
        if f.is_valid():
            results = []
            facts = []
            for fact in f.cleaned_data['facts']:
                facts.append(fact.name)
            facts.sort()

            for host in f.cleaned_data['hosts']:
                d = {}
                row = []
                values = host.factvalue_set.filter(fact_name__in=f.cleaned_data['facts'])
                for val in values:
                    if val.fact_name.name in d:
                        d[val.fact_name.name] += ", %s" % val.value
                    else:
                        d[val.fact_name.name] = val.value

                for fact in facts:
                    row.append(d.get(fact,None))
                results.append({'host': host, 'facts': row })
                    
            return render_to_response("query_results.html", { 'facts': facts, 'results': results })
        else:
            return render_to_response("query.html", { 'form': f })
