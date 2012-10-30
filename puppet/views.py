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

from servermon.puppet.models import FactValue
from servermon.compat import render

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

    return render(request, "inventory.html", {'hosts': hosts})
