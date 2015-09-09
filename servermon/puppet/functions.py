# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
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
Module contains functions for performing searches in puppet

Important function here is search(q) which searches strings or iterables of
strings in puppet models.
'''

from puppet.models import FactValue
from django.db import DatabaseError
from django.db.models import Q
from django.utils.translation import ugettext as _
from django.conf import settings


def search(q):
    '''
    Searches in Puppet models model for various info

    @type  q: string or iterable
    @param q: a string or an iterable of strings to search for.

    @rtype: QuerySet
    @return: A QuerySet with results matching all items of q
    '''

    if q is None or len(q) == 0 or 'puppet' not in settings.INSTALLED_APPS:
        return FactValue.objects.none()

    # Working on iterables. However in case we are not given one it is cheaper
    # to create one than fail
    try:
        q.__iter__()
    except AttributeError:
        q = (q,)

    ids = []

    try:
        for key in q:
            base = FactValue.objects.filter(value__icontains=key)
            base = base.filter(
                Q(fact_name__name='fqdn') |
                Q(fact_name__name__startswith='macaddress_') |
                Q(fact_name__name__startswith='ipaddress_') |
                Q(fact_name__name__startswith='ipaddress6_') |
                Q(fact_name__name__startswith='lldpswport_') |
                Q(fact_name__name='lldpparents') |
                Q(fact_name__name='manufacturer') |
                Q(fact_name__name='productname') |
                Q(fact_name__name='puppetclass') |
                Q(fact_name__name='system_serial_number') |
                Q(fact_name__name='ipmi_dns') |
                Q(fact_name__name='ipmi_ipaddress') |
                Q(fact_name__name='ipmi_macaddress') |
                Q(fact_name__name='rackunit')
            )
            ids.extend(base.distinct().values_list('id', flat=True))
        ids = list(set(ids))
        ret = FactValue.objects.filter(pk__in=ids)
        ret = ret.distinct().order_by('host__name')
        return ret
    except DatabaseError as e:
        return FactValue.objects.none()
        # TODO: Log this
        raise RuntimeError(_('An error occured while querying db: %(databaseerror)s') % {'databaseerror': e})
