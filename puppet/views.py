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

from puppet.models import *
from django.shortcuts import render_to_response, get_object_or_404
from django.db.models import Q
from IPy import IP

def index(request):
    hosts = Host.objects.order_by('name')
    return render_to_response("index.html", { 'hosts': hosts })

def host(request, host=None):
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
    system.append({ 'name': 'Serial Nr.',
        'value': host.get_fact_value('serialnumber')
        })
    system.append({ 'name': 'Memory',
        'value': "%s (%s free)" % (host.get_fact_value('memorysize'), host.get_fact_value('memoryfree'))
        })
    system.append({ 'name': 'Processors',
        'value': host.get_fact_value('processorcount')
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

    return render_to_response("host.html", { 'host': host, 'interfaces': interfaces, 'system': system })

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
