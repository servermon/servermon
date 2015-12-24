# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2012 Faidon Liambotis
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
updates views module
'''

from django.shortcuts import get_list_or_404, get_object_or_404
from django.shortcuts import render
from django.db.models import Count
from puppet.models import Host
from updates.models import Package, Update
from hwdoc.models import Equipment
from IPy import IP
from collections import OrderedDict


def hostlist(request):
    hosts = Host.objects.annotate(update_count=Count('update'))
    security_updates = Host.objects.filter(
        update__is_security=True).annotate(security_count=Count('package'))

    # Create a temporary structure to merge those 2 structures. Use OrderedDict
    # to preserve the order returned by the QuerySet
    hosts = OrderedDict(map(
        lambda x: (x['name'], x),
        hosts.values('name', 'update_count')
    ))
    security_updates = dict(map(
        lambda x: (x['name'], x),
        security_updates.values('name', 'security_count')
    ))
    for k, v in hosts.items():
        if k in security_updates:
            v.update(security_updates[k])
    # And now get the final data structure
    hosts = hosts.values()
    return render(request, 'hostlist.html', {'hosts': hosts})


def packagelist(request):
    packages = Package.objects.annotate(host_count=Count('hosts'))
    security_updates = Package.objects.filter(
        update__is_security=True).annotate(security_count=Count('hosts'))

    # Create a temporary structure to merge those 2 structures. Use OrderedDict
    # to preserve the order returned by the QuerySet
    packages = OrderedDict(map(
        lambda x: (x['name'], x),
        packages.values('name', 'host_count')
    ))
    security_updates = dict(map(
        lambda x: (x['name'], x),
        security_updates.values('name', 'security_count')
    ))
    for k, v in packages.items():
        if k in security_updates:
            v.update(security_updates[k])
    # And now getting the final data structure
    packages = packages.values()
    return render(request, 'packagelist.html', {'packages': packages})


def package(request, packagename):
    # there may be multiple Package with same name but different sourcename
    package = get_list_or_404(Package, name=packagename)[0]

    updates = package.update_set.order_by('host__name')
    if "plain" in request.GET:
        return render(request, "package.txt", {"updates": updates}, content_type="text/plain")
    return render(request, 'packageview.html', {'package': package, 'updates': updates})


def host(request, hostname):
    host = get_object_or_404(Host, name=hostname)

    updates = []
    system = []
    location = []

    try:
        iflist = host.get_fact_value('interfaces').split(',')
    except AttributeError:
        iflist = []

    # Network part
    interfaces = []
    for iface in iflist:
        d = {}
        iface1 = iface.replace(':', '_')
        mac = host.get_fact_value('macaddress_%s' % iface1)
        ip = host.get_fact_value('ipaddress_%s' % iface1)
        netmask = host.get_fact_value('netmask_%s' % iface1)
        ip6 = host.get_fact_value('ipaddress6_%s' % iface1)

        d = {'iface': iface,
             'mac': mac}

        if netmask and ip:
            d['ipaddr'] = '%s/%d' % (ip, IP(ip).make_net(netmask).prefixlen())

        if ip6:
            d['ipaddr6'] = ip6

        interfaces.append(d)

    # System part
    fields = [
        ('bios_date', 'BIOS Date'),
        ('bios_version', 'BIOS Version'),
        ('manufacturer', 'System Vendor'),
        ('productname', 'Model'),
        ('serialnumber', 'Serial number'),
        ('processorcount', 'Processors'),
        ('architecture', 'Architecture'),
        ('virtual', 'Machine Type'),
        ('uptime', 'Uptime'),
    ]
    attrs = (
        {
            'name': 'Rack Unit',
            'value': lambda x: '%s' % x.unit
        },
        {
            'name': 'Rack',
            'value': lambda x: '%s' % x.rack,
            'link': lambda x: '%s' % x.rack.get_absolute_url()
        },
        {
            'name': 'Rack Row',
            'value': lambda x: '%s' % x.rack.rackposition.rr
        },
        {
            'name': 'IPMI Method',
            'value': lambda x: '%s' % x.servermanagement.method
        },
        {
            'name': 'IPMI Hostname',
            'value': lambda x: '%s' % x.servermanagement.hostname,
            'link': lambda x: 'https://%s' % x.servermanagement.hostname
        },
        {
            'name': 'IPMI MAC',
            'value': lambda x: '%s' % x.servermanagement.mac
        },
        {
            'name': 'Datacenter',
            'value': lambda x: '%s' % x.rack.rackposition.rr.dc,
            'link': lambda x: '%s' % x.rack.rackposition.rr.dc.get_absolute_url()
        },
    )

    for fact, label in fields:
        system.append({'name': label, 'value': host.get_fact_value(fact)})

    system.append({
        'name': 'Processor type',
        'value': ', '.join([p['value'] for p in host.factvalue_set.filter(fact_name__name__startswith='processor').exclude(fact_name__name='processorcount').values('value').distinct()]),
    })

    system.append({
        'name': 'Operating System',
        'value': '%s %s' % (host.get_fact_value('operatingsystem'), host.get_fact_value('operatingsystemrelease'))
    })
    system.append({
        'name': 'Memory',
        'value': '%s (%s free)' % (host.get_fact_value('memorytotal'), host.get_fact_value('memoryfree'))
    })

    # Location info part
    try:
        eq = Equipment.objects.get(serial=host.get_fact_value('serialnumber'))
    except Equipment.DoesNotExist:
        location.append({
            'name': 'Location',
            'value': '%s' % 'No location information found'
        })
        eq = None
    if eq:
        for attr in attrs:
            try:
                tmp = {
                    'name': attr['name'],
                    'value': attr['value'](eq)
                }
            except:
                continue
            try:
                tmp['link'] = attr['link'](eq)
            except:
                pass
            location.append(tmp)
    # Updates info
    updates = Update.objects.filter(host=host).order_by('package__name')
    updates = updates.select_related()

    return render(request, 'hostview.html', {
        'host': host,
        'updates': updates,
        'interfaces': interfaces,
        'system': system,
        'location': location,
    })
