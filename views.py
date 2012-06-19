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

from servermon.puppet.models import Host, Fact, FactValue
from servermon.updates.models import Package, Update
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, Http404
from datetime import datetime, timedelta
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from settings import HOST_TIMEOUT
from IPy import IP
import re

def host(request,hostname):
    host = get_object_or_404(Host, name=hostname)

    updates = []
    system = []

    iflist = host.get_fact_value('interfaces').split(',')
    interfaces = []
    for iface in iflist:
        d = {}
        iface1 = iface.replace(':','_')
        mac = host.get_fact_value('macaddress_%s' % iface1)
        ip = host.get_fact_value('ipaddress_%s' % iface1)
        netmask = host.get_fact_value('netmask_%s' % iface1)
        ip6 = host.get_fact_value('ipaddress6_%s' % iface1)

        d = { 'iface': iface,
              'mac': mac }

        if netmask and ip:
            d['ipaddr'] = "%s/%d" % (ip, IP(ip).make_net(netmask).prefixlen())

        if ip6:
            d['ipaddr6'] = ip6

        interfaces.append(d)

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
        'value': "%s (%s free)" % (host.get_fact_value('memorytotal'), host.get_fact_value('memoryfree'))
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
    keys = [
        'is_virtual',
        'manufacturer',
        'productname',
        'bios_date',
        'bios_version',
        'serialnumber',
        'architecture',
        'processorcount',
        'memorytotal',
    ]

    # This could be more normally be expressed starting with Host as the base
    # model, since we are essentially asking for hosts plus their facts.
    #
    # However, Django's select_related doesn't traverse reverse foreign keys,
    # and hence we were forced to do one fact query per host, i.e N+1 queries.
    #
    # Django 1.4 has prefetch_related() which may or may not help; until then
    # work around the ORM and combine it with itertools.groupby(). Should
    # still have a performance hit for, say, more than 1k hosts.

    facts = FactValue.objects.all()
    facts = facts.filter(fact_name__name__in=keys)
    facts = facts.order_by('host') # itertools.groupby needs sorted input
    facts = facts.select_related() # performance optimization

    hosts = []
    from itertools import groupby
    for key, values in groupby(facts, key=lambda x: x.host.name):
        host = {'name': key }
        for v in values:
            host[v.name] = v.value
        hosts.append(host)

    return render_to_response("inventory.html", {'hosts': hosts})

def index(request):
    timeout = datetime.now() - timedelta(seconds=HOST_TIMEOUT)

    hosts = Host.objects.all()
    problemhosts = Host.objects.filter(updated_at__lte=timeout).order_by('name')
    factcount = Fact.objects.count()
    factvaluecount = FactValue.objects.count()
    updatecount = Host.objects.filter(package__isnull=False).distinct().count()
    packagecount = Package.objects.count()

    return render_to_response("index.html", {
        'problemhosts': problemhosts, 
        'timeout': timeout,
        'hosts': hosts,
        'factcount': factcount,
        'factvaluecount': factvaluecount,
        'updatecount': updatecount,
        'packagecount': packagecount,
        })

def search(request):
    if not request.POST or (not 'search' in request.POST):
        return HttpResponseRedirect('/')

    fieldmap = [
            ('Hostname', 'fqdn'),
            ('MAC Address', 'macaddress_'),
            ('IPv4 Address', 'ipaddress_'),
            ('IPv6 Address', 'ipaddress6_'),
            ('Vendor', 'manufacturer'),
            ('Model', 'productname'),
            ('Puppet class', 'puppetclass'),
            ('Operating system', 'operatingsystem')
            ]
    
    matches = []
    regex = re.compile(r'(' + request.POST['search'] + ')', re.IGNORECASE)

    base = FactValue.objects.filter(value__icontains=request.POST['search'])
    base = base.distinct().order_by('host__name')

    for name, field in fieldmap:
        res = base
        if field.endswith('_'):
            res = res.filter(fact_name__name__startswith=field)
        else:
            res = res.filter(fact_name__name=field)
        res = res.select_related()

        for r in res:
            matches.append({
                'name': r.host.name,
                'attribute': name,
                'value': regex.sub(r'<strong>\1</strong>', r.value),
                })

    return render_to_response("search.html", {
            'matches': matches,
            'search': request.POST['search']
            })

def query(request):
    class MatrixForm(forms.Form):
        hosts = forms.ModelMultipleChoiceField(queryset=Host.objects.all(),
                widget=FilteredSelectMultiple("hosts", is_stacked=False))
        facts = forms.ModelMultipleChoiceField(queryset=Fact.objects.all()
                    .exclude(name__startswith='---')        # ruby objects
                    .exclude(name__startswith='macaddress') # VMs have tons of network interfaces :/
                    .exclude(name__startswith='ipaddress')
                    .exclude(name__startswith='ipaddress6')
                    .exclude(name__startswith='network')
                    .exclude(name__startswith='netmask'),
                widget=FilteredSelectMultiple("parameters", is_stacked=False))

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

            values = FactValue.objects.all()
            values = values.filter(fact_name__in=f.cleaned_data['facts'])
            values = values.filter(host__in=f.cleaned_data['hosts'])
            values = values.order_by('host') # itertools.groupby needs sorted input
            values = values.select_related() # performance optimization

            from itertools import groupby
            for key, values in groupby(values, key=lambda x: x.host.name):
                row = {}
                for v in values:
                    row[v.name] = v.value
                row = [ row.get(k, None) for k in facts ]
                results.append({'host': key, 'facts': row })

            return render_to_response("query_results.html", { 'facts': facts, 'results': results })
        else:
            return render_to_response("query.html", { 'form': f })
