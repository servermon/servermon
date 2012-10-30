# -*- coding: utf-8 -*- vim:encoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2012 Faidon Liambotis
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
from django.shortcuts import get_object_or_404
from servermon.compat import render
from django.http import HttpResponseRedirect, Http404
from datetime import datetime, timedelta
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms
from settings import HOST_TIMEOUT, INSTALLED_APPS
from IPy import IP
import re

def index(request):
    timeout = datetime.now() - timedelta(seconds=HOST_TIMEOUT)

    hosts = Host.objects.all()
    problemhosts = Host.objects.filter(updated_at__lte=timeout).order_by('-updated_at')
    factcount = Fact.objects.count()
    factvaluecount = FactValue.objects.count()
    updatecount = Host.objects.filter(package__isnull=False).distinct().count()
    packagecount = Package.objects.count()
    securitycount = Package.objects.filter(update__is_security=True).distinct().count()
    if 'servermon.hwdoc' in INSTALLED_APPS:
        hwdoc_installed = True
    else:
        hwdoc_installed = False

    return render(request, "index.html", {
        'problemhosts': problemhosts, 
        'timeout': timeout,
        'hosts': hosts,
        'factcount': factcount,
        'factvaluecount': factvaluecount,
        'updatecount': updatecount,
        'packagecount': packagecount,
        'securitycount': securitycount,
        'hwdoc_installed': hwdoc_installed,
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

    return render(request, "search.html", {
            'matches': matches,
            'search': request.POST['search']
            })

def query(request):
    class MatrixForm(forms.Form):
        hosts = forms.ModelMultipleChoiceField(queryset=Host.objects.all(),
                widget=FilteredSelectMultiple("hosts", is_stacked=False))
        facts = forms.ModelMultipleChoiceField(queryset=Fact.objects.all()
                    .exclude(name__startswith='---')        # ruby objects
                    .exclude(name__startswith='package_updates')
                    .exclude(name__startswith='macaddress_') # VMs have tons of network interfaces :/
                    .exclude(name__startswith='ipaddress_')
                    .exclude(name__startswith='ipaddress6_')
                    .exclude(name__startswith='network_')
                    .exclude(name__startswith='netmask_'),
                widget=FilteredSelectMultiple("parameters", is_stacked=False))

    if request.method == 'GET':
        f = MatrixForm(label_suffix='')
        return render(request, "query.html", { 'form': f })
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

            return render(request, "query_results.html", { 'facts': facts, 'results': results })
        else:
            return render(request, "query.html", { 'form': f })
