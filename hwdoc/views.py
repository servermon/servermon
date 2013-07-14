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
hwdoc views module
'''

from servermon.hwdoc.models import Project, EquipmentModel, Equipment, \
        ServerManagement, Rack, RackRow, Datacenter, RackPosition, Vendor
from servermon.projectwide import functions as projectwide_functions
from servermon.hwdoc import functions
from servermon.compat import render
from django.shortcuts import get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest
from django.core import serializers
from django.db.models import Count
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

    if request.is_ajax() == False:
        return HttpResponseBadRequest('Not an AJAX request',
        content_type='text/plain')

    # It might seem like overkill, but only one of them will actually be
    # realized. The rest are lazy Querysets
    switch = {
        'datacenters': Datacenter.objects.all(),
        'racks': Rack.objects.order_by('id').all(),
        'projects': Project.objects.order_by('name').all(),
        'rackrows': RackRow.objects.order_by('id').all(),
        'models': EquipmentModel.objects.order_by('name').all(),
    }
    keys = {
        'datacenters': '"pk"',
        'racks': '"pk"',
        'projects': '"pk"',
        'rackrows': '"pk"',
        'models': '"name"',
    }

    if subnav not in switch.keys():
        return HttpResponseBadRequest('[{"error": "Incorrect subnav specified"}]',
                content_type='application/json')

    data = serializers.serialize('json', switch[subnav])

    return HttpResponse('{ "key": %s, "val": %s}' % (keys[subnav], data),
                            content_type="application/json")

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

    if request.is_ajax() == False:
        return HttpResponseBadRequest('Not an AJAX request',
        content_type='text/plain')

    with_comments = { 'name': 'With' }
    without_comments = { 'name': 'Without' }
    with_comments.update(Equipment.objects.exclude(comments='').aggregate(num_equipment=Count('comments')))
    without_comments.update(Equipment.objects.filter(comments='').aggregate(num_equipment=Count('comments')))

    switch = {
        'datacenters': Datacenter.objects.annotate(num_equipment=Count('rackrow__rackposition__rack__equipment')).values('name','num_equipment'),
        'projects': Project.objects.annotate(num_equipment=Count('equipment')).values('name','num_equipment'),
        'vendors': Vendor.objects.annotate(num_equipment=Count('equipmentmodel__equipment')).values('name','num_equipment'),
        'models': EquipmentModel.objects.annotate(num_equipment=Count('equipment')).values('name','num_equipment'),
        'comments': (with_comments, without_comments),
        'tickets': Project.objects.annotate(num_equipment=Count('equipment')).values('name','num_equipment'),
    }
    if datatype not in switch.keys():
        return HttpResponseBadRequest('[{"error": "Incorrect datatype specified"}]',
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

def equipment(request, equipment_id):
    '''
    Equipment view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'equipment.html'

    equipment = get_object_or_404(Equipment,pk=equipment_id)
    equipment = functions.populate_tickets((equipment,))[0]
    try:
        equipment.prev = Equipment.objects.filter(rack=equipment.rack, unit__lt=equipment.unit).order_by('-unit')[0]
    except IndexError:
        equipment.prev = None
    try:
        equipment.next = Equipment.objects.filter(rack=equipment.rack, unit__gt=equipment.unit).order_by('unit')[0]
    except IndexError:
        equipment.next = None

    return render(request, template, { 'equipment': equipment, })

def project(request, project_id):
    '''
    Project view. It should display all non-authenticated user viewable data

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    template = 'project.html'

    project = get_object_or_404(Project,pk=project_id)
    equipments = { 'hwdoc': functions.search(project.name) }
    return render(request, template, { 'project': project, 'equipments': equipments })

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

    equipments = functions.search(str(rack.name))
    equipments = functions.populate_tickets(equipments)
    equipments = functions.populate_hostnames(equipments)

    # The rendering expects this form.
    equipments = { 'hwdoc': equipments, }

    return render(request, template, { 'rack': rack, 'equipments': equipments })

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
        rack.equipments = functions.populate_tickets(
                rack.rack.equipment_set.select_related('model__vendor', 'model'))
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
    for rackrow in rackrows:
        racks = [str(x).zfill(2) for x in
                rackrow.rackposition_set.values_list('rack__pk', flat=True)]
        equipments = functions.search(racks)
        equipments = equipments.exclude(comments='')
        if equipments.count() > 0:
            rackrow.tickets = True
    return render(request, template, {
        'datacenter': datacenter,
        'rackrows': rackrows,
        })

