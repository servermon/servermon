# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
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

'''
Module contains functions for performing searches in hwdoc

Important function here is search(q) which searches strings or iterables of
strings in model Equipment.
'''

from hwdoc.models import Equipment, ServerManagement
from projectwide.functions import canonicalize_mac
from puppet.functions import search as puppet_search
from django.db.models import Q
from socket import gethostbyaddr, herror, gaierror, error
from django.utils.translation import ugettext as _
from django.conf import settings
from django.db import DatabaseError
import re

def search(q):
    '''
    Searches in Equipment model for racks, units, IP address, MACs, serial, hostnames etc

    @type  q: string or iterable
    @param q: a string or an iterable of strings to search for.

    @rtype: QuerySet
    @return: A QuerySet with results matching all items of q
    '''

    if q is None or len(q) == 0 or 'hwdoc' not in settings.INSTALLED_APPS:
        return Equipment.objects.none()

    # A way to get all
    if q == "ALL_EQS":
        return Equipment.objects.all()

    # Working on iterables. However in case we are not given one it is cheaper
    # to create one than fail
    try:
        q.__iter__()
    except AttributeError:
        q = (q,)

    ids = []

    try:
        for key in q:
            try:
                dns = gethostbyaddr(key)[0]
            except (herror, gaierror, IndexError, error, UnicodeEncodeError):
                dns = ''
            mac = canonicalize_mac(key)
            # A heuristic to allow user to filter queries down to the unit level
            # using a simple syntax
            m = re.search('^(\w?\d\d)[Uu]?(\d\d)$', key)
            if m:
                rack = m.group(1)
                unit = m.group(2)
            else:
                rack = ''
                unit = None

            result = Equipment.objects.filter(
                                            Q(serial=key)|
                                            Q(rack__name__contains=key)|
                                            Q(rack__name__iexact=rack)|
                                            Q(model__name__icontains=key)|
                                            Q(allocation__name__icontains=key)|
                                            Q(allocation__contacts__name__icontains=key)|
                                            Q(allocation__contacts__surname__icontains=key)|
                                            Q(servermanagement__mac__icontains=mac)|
                                            Q(servermanagement__hostname__icontains=key)|
                                            Q(servermanagement__hostname=dns)|
                                            Q(attrs__value__icontains=key)
                                            )
            if unit:
                result = result.filter(unit=unit)
            ids.extend(result.distinct().values_list('id', flat=True))
            ids = list(set(ids))
            return Equipment.objects.filter(pk__in=ids).distinct()
    except DatabaseError as e:
        return Equipment.objects.none()
        # TODO: Log this
        raise RuntimeError(_('An error occured while querying db: %(databaseerror)s') % {'databaseerror': e})

def populate_tickets(equipment_list, closed=False):
    '''
    Populates tickets attribute for each equipment in a queryset.

    Note: This function creates an abstration by using the vendor submodule
    and the ticketing systems defined there.
    This function WILL evaluate the queryset and cause database lookups.

    @type  equipment_list: Queryset
    @param equipment_list: A Django queryset containing equipment which need to
    be populated with tickets attribute

    @rtype: QuerySet
    @return: A QuerySet with equipment's comments attribute populated
    '''

    try:
        vm = __import__('hwdoc.vendor.ticket_%s' % settings.TICKETING_SYSTEM,
                        fromlist=['hwdoc.vendor'])
    except ImportError as e:
        # TODO: Log ther error. For now just print
        print e
        return equipment_list

    for equipment in equipment_list:
        try:
            getattr(vm, 'get_tickets')(equipment, closed)
        except AttributeError as e:
            # TODO: Log the error. For now just print
            print e
            return equipment_list
    return equipment_list

def populate_hostnames(equipment_list):
    '''
    Populates hostnames if they exist from puppet app for each equipment in a queryset.

    @type  equipment_list: Queryset
    @param equipment_list: A Django queryset containing equipment which need to
    be populated with hostname attribute

    @rtype: QuerySet
    @return: A QuerySet with equipment's hostname attribute populated
    '''

    serials = equipment_list.values_list('serial', flat=True)
    factvalues = puppet_search(serials)
    factvalues = factvalues.filter(fact_name__name__contains='serial')

    # We evaluate our querysets cause we would hit way too much the database
    # afterwards
    eqs = list(equipment_list)
    factvalues = list(factvalues)

    factvalues = dict(map(lambda x: (x.value.strip(), x.host.name), factvalues))

    for eq in eqs:
        eq.hostname = None
        try:
            eq.hostname = factvalues[eq.serial]
        except:
            pass
    return equipment_list

def calculate_empty_units(rack, equipment_list):
    '''
    Calculates the empty units in a rack and adds virtual equipments with the
    only attribute being unit. The result is not meant to be correct QuerySet

    @type  rack: Rack
    @param rack: An Instance of Model Rack
    @type  equipment_list: Queryset
    @param equipment_list: A Django queryset containing equipment that indeed is
    on the rack

    @rtype: QuerySet
    @return: A QuerySet with virtual equipments added to
    '''

    units = []
    for z in ((x+w for w in xrange(y)) for x,y in equipment_list.values_list('unit', 'model__u')):
        units.extend(z)
    empty_units = set(rack.model.units) - set(sorted(units))
    equipment_list = list(equipment_list)

    for empty_unit in empty_units:
        equipment_list.append(Equipment(unit=empty_unit, rack=rack))

    return sorted(equipment_list, key=lambda eq: eq.unit, reverse=True)
