# -*- coding: utf-8 -*- vim:encoding=utf-8:
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

from puppet.models import Host, Fact, FactValue
from updates.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from settings import HOST_TIMEOUT
from IPy import IP
import re

def host(request,hostname):
    host = get_object_or_404(Host, name=hostname)

    updates = []
    system = []

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

    updates = host.update_set.order_by('package__name')

    return render_to_response('hostview.html', {
        'host': host,
        'updates': updates,
        'interfaces': interfaces,
        'system': system,
        })


def inventory(request):
    hosts = Host.objects.filter(factvalue__fact_name__name='is_virtual').exclude(factvalue__value='true')

    hostlist = []
    for host in hosts:
        hostlist.append({
            'name': host.name,
            'manufacturer': host.get_fact_value('manufacturer'),
            'productname': host.get_fact_value('productname'),
            'biosdate': host.get_fact_value('bios_date'),
            'biosversion': host.get_fact_value('bios_version'),
            'serial': host.get_fact_value('serialnumber'),
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
    for name, field in [('Hostname', 'fqdn'), ('MAC Address', 'macaddress_'), ('IP Address', 'ipaddress_'), ('Vendor', 'manufacturer'), ('Model', 'productname'), ('Puppet class', 'puppetclass'), ('Operating system', 'operatingsystem')]:
        res = FactValue.objects.filter(fact_name__name__startswith=field, value__icontains=request.POST['search']).distinct().order_by('host__name')
        for r in res:
            matches.append({'name': r.host.name, 'attribute': name, 'value': regex.sub(r'<strong>\1</strong>', r.value)})

    return render_to_response("search.html", {'matches': matches , 'search': request.POST['search']})


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
