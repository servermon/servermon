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
hwdoc views module
'''

from hwdoc.models import Project, EquipmentModel, Equipment, \
    Rack, RackRow, Datacenter, RackPosition, Vendor, \
    Storage
from hwdoc import functions
from django.shortcuts import render
from django.http import HttpResponse, HttpResponseBadRequest
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.core.urlresolvers import reverse
from django.http import Http404
import json


def subnav(request, subnav):
    '''
    hwdoc index page navigation view. XMLHttpRequest (aka AJAX) only view

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @type   subnav: String
    @param  request: description of an hwdoc entity requesting listing
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding JSON
    '''

    if request.is_ajax() is False:
        return HttpResponseBadRequest(
            'Not an AJAX request', content_type='text/plain')

    # It might seem like overkill, but only one of them will actually be
    # realized. The rest are lazy Querysets
    switch = {
        'datacenters': Datacenter.objects.all(),
        'racks': Rack.objects.order_by('name').all(),
        'projects': Project.objects.order_by('name').all(),
        'rackrows': RackRow.objects.order_by('id').all(),
        'models': EquipmentModel.objects.order_by('name').all(),
    }
    urls = {
        'datacenters': {'view': 'hwdoc.views.datacenter', 'args': 'pk', 'append': None},
        'racks': {'view': 'hwdoc.views.rack', 'args': 'pk', 'append': None},
        'projects': {'view': 'hwdoc.views.project', 'args': 'pk', 'append': None},
        'rackrows': {'view': 'hwdoc.views.rackrow', 'args': 'pk', 'append': None},
        'models': {'view': 'projectwide.views.search', 'args': None, 'append': 'q='},
    }

    if subnav not in switch.keys():
        return HttpResponseBadRequest(
            '[{"error": "Incorrect subnav specified"}]',
            content_type='application/json')

    data = switch[subnav]
    # This is difficult to read. It creates the json response to send based on
    # two different ifs inside a reverse, inside a lambda. Should be rewritten
    # at some point
    data = map(
        lambda x: {
            'name': x.name,
            'url': reverse(  # noqa
                urls[subnav]['view'],
                args=(getattr(x, urls[subnav]['args']),) if urls[subnav]['args'] else None) +
                ('?%s%s' % (urls[subnav]['append'], x.name) if urls[subnav]['append'] else '')
        }, data)
    data = json.dumps(data)

    return HttpResponse(data, content_type='application/json')


def flotdata(request, datatype):
    '''
    hwdoc flot data view. XMLHttpRequest (aka AJAX) only view

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @type   datatype: String
    @param  request: description of an hwdoc entity requesting listing
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding JSON
    '''

    if request.is_ajax() is False:
        return HttpResponseBadRequest(
            'Not an AJAX request', content_type='text/plain')

    with_comments = {'name': 'With'}
    without_comments = {'name': 'Without'}
    with_comments.update({'num_equipment': Equipment.objects.exclude(comments='').count()})
    without_comments.update({'num_equipment': Equipment.objects.filter(comments='').count()})
    with_tickets = {'name': 'With'}
    without_tickets = {'name': 'Without'}
    with_tickets.update({'num_equipment': Equipment.objects.filter(ticket__isnull=False).count()})
    without_tickets.update({'num_equipment': Equipment.objects.filter(ticket__isnull=True).count()})

    switch = {
        'datacenters': Datacenter.objects.annotate(num_equipment=Count('rackrow__rackposition__rack__equipment')).values('name', 'num_equipment'),
        'projects': Project.objects.annotate(num_equipment=Count('equipment')).values('name', 'num_equipment'),
        'vendors': Vendor.objects.annotate(num_equipment=Count('equipmentmodel__equipment')).values('name', 'num_equipment'),
        'models': EquipmentModel.objects.annotate(num_equipment=Count('equipment')).values('name', 'num_equipment'),
        'comments': (with_comments, without_comments),
        'tickets': (with_tickets, without_tickets)
    }
    if datatype not in switch.keys():
        return HttpResponseBadRequest(
            '[{"error": "Incorrect datatype specified"}]',
            content_type='application/json')

    data = map(lambda x: {'label': x['name'], 'data': x['num_equipment']}, switch[datatype])

    return HttpResponse(json.dumps(data), content_type="application/json")


def index(request):
    '''
    hwdoc index view

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    return render(request, 'hwdocindex.html')


def unallocated_equipment(request):
    '''
    Unallocated Equipment view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''
    template = 'interesting_equipment.html'

    equipments = {'hwdoc': Equipment.objects.filter(allocation__isnull=True).distinct()}
    return render(request, template, {'equipments': equipments})


def commented_equipment(request):
    '''
    Equipment with comments view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''
    template = 'interesting_equipment.html'

    equipments = {'hwdoc': Equipment.objects.exclude(comments='').distinct()}
    return render(request, template, {'equipments': equipments})


def ticketed_equipment(request):
    '''
    Equipment with tickets view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''
    template = 'interesting_equipment.html'

    equipments = Equipment.objects.filter(ticket__isnull=False).distinct()
    equipments = {'hwdoc': equipments}
    return render(request, template, {'equipments': equipments})


def unracked_equipment(request):
    '''
    Equipment that is not mounted into a rack. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''
    template = 'interesting_equipment.html'

    equipments = Equipment.objects.filter(rack__isnull=True).distinct()
    equipments = {'hwdoc': equipments}
    return render(request, template, {'equipments': equipments})


def equipment(request, equipment_input):
    '''
    Equipment view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'equipment.html'

    # If we got an int, it's either a PK or a serial
    try:
        int(equipment_input)
        equipment = Equipment.objects.get(
            Q(pk=equipment_input) |
            Q(serial=equipment_input)
        )
    except Equipment.DoesNotExist:
        raise Http404
    except ValueError:
        # Otherwise it's a serial
        try:
            equipment = Equipment.objects.get(serial=equipment_input)
        except Equipment.DoesNotExist:
            # Otherwise it's nothing
            raise Http404
    # If not 404's got raised up to now, we got an equipment
    try:
        equipment.prev = Equipment.objects.filter(rack=equipment.rack, unit__lt=equipment.unit).order_by('-unit')[0]
    except (IndexError, ValueError):
        equipment.prev = None
    try:
        equipment.next = Equipment.objects.filter(rack=equipment.rack, unit__gt=equipment.unit).order_by('unit')[0]
    except (IndexError, ValueError):
        equipment.next = None

    return render(request, template, {'equipment': equipment})


def project(request, project_id):
    '''
    Project view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'project.html'

    project = get_object_or_404(Project, pk=project_id)
    equipments = {'hwdoc': functions.search(project.name)}
    return render(request, template, {'project': project, 'equipments': equipments})


def rack(request, rack_id):
    '''
    Rack view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'rack.html'

    rack = get_object_or_404(Rack, pk=rack_id)
    try:
        rack.prev = Rack.objects.filter(
            rackposition__position__lt=rack.rackposition.position,
            rackposition__rr=rack.rackposition.rr
        ).order_by('-rackposition__position')[0]
    except (IndexError, RackPosition.DoesNotExist):
        rack.prev = None
    try:
        rack.next = Rack.objects.filter(
            rackposition__position__gt=rack.rackposition.position,
            rackposition__rr=rack.rackposition.rr
        ).order_by('rackposition__position')[0]
    except (IndexError, RackPosition.DoesNotExist):
        rack.next = None

    equipments = rack.equipment_set.all()
    equipments = functions.populate_hostnames(equipments)
    equipments = list(equipments)
    equipments.extend(map(
        lambda x: Equipment(unit=x, rack=rack),
        rack.get_empty_units()))
    equipments = sorted(equipments, key=lambda eq: eq.unit, reverse=True)

    equipments = {'hwdoc': [e for e in equipments if e.unit > 0],
                  'hwdoc_zero_u': [e for e in equipments if e.unit == 0], }

    return render(request, template, {'rack': rack, 'equipments': equipments})


def rackrow(request, rackrow_id):
    '''
    Rackrow view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'rackrow.html'

    rackrow = get_object_or_404(RackRow, pk=rackrow_id)
    racks = rackrow.rackposition_set.select_related()
    for rack in racks:
        equipments = rack.rack.equipment_set.all().select_related(
            'model__vendor',
            'model',
        )
        equipments = list(equipments)
        equipments.extend(map(
            lambda x: Equipment(unit=x, rack=rack.rack),
            rack.rack.get_empty_units()))
        rack.equipments = sorted(equipments, key=lambda eq: eq.unit, reverse=True)
    return render(request, template, {
        'rackrow': rackrow,
        'racks': racks,
    })


def datacenter(request, datacenter_id):
    '''
    Rackrow view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'datacenter.html'

    datacenter = get_object_or_404(Datacenter, pk=datacenter_id)
    rackrows = datacenter.rackrow_set.all()
    storages = datacenter.storage_set.all()
    for rackrow in rackrows:
        equipments = Equipment.objects.filter(rack__rackposition__rr__name=rackrow.name)
        equipments = equipments.exclude(ticket__isnull=True)
        if equipments.count() > 0:
            rackrow.tickets = True
    return render(request, template, {
        'datacenter': datacenter,
        'rackrows': rackrows,
        'storages': storages,
    })


def storage(request, storage_id):
    '''
    Storage view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'storage.html'

    storage = get_object_or_404(Storage, pk=storage_id)
    equipments = storage.equipment_set.all()
    return render(request, template, {
        'equipments': {'hwdoc': equipments},
    })
