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
        ServerManagement, Rack, RackRow, Datacenter
from servermon.hwdoc import functions
from servermon.compat import render
from django.shortcuts import get_object_or_404
from django.conf import settings
from django.contrib.sites.models import Site
from django.utils import simplejson
from django.http import HttpResponse

def index(request):
    '''
    hwdoc index view

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    datacenters = Datacenter.objects.all()
    racks = Rack.objects.order_by('id').all()
    projects = Project.objects.order_by('name').all()
    models = EquipmentModel.objects.select_related('vendor').order_by('vendor__name','name').all()
    
    return render(request, 'hwdocindex.html', {
                'racks': racks,
                'projects': projects,
                'models': models,
                'datacenters': datacenters,
            })

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
    return render(request, template, { 'project': project, })

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
    equipments = functions.search(str(rack.pk))
    equipments = functions.populate_tickets(equipments)

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

def search(request):
    '''
    Search view. Scans request for q (GET case) or qarea (POST case) and
    searches for corresponding Equipment instances matching the query
    If txt is send in a GET it will display results in txt and not in html
    format

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    if u'txt' in request.GET:
        template = 'results.txt'
        mimetype = 'text/plain'
    else:
        template = 'results.html'
        mimetype = 'text/html'

    if u'q' in request.GET:
        key = request.GET['q']
    elif u'qarea' in request.POST:
        key = functions.get_search_terms(request.POST['qarea'])
    else:
        key = None

    results = functions.search(key).select_related(
            'servermanagement', 'rack', 'model',
            'model__vendor', 'allocation') 

    results = functions.populate_tickets(results)

    return render(request, template,
            { 'results': results, },
            mimetype=mimetype)

def advancedsearch(request):
    '''
    Advanced search view. Renders free text search

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    return render(request, 'advancedsearch.html')

def opensearch(request):
    '''
    opensearch search view. Renders opensearch.xml

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding XML
    '''

    fqdn = Site.objects.get_current().domain
    try:
        contact = settings.ADMINS[0][0]
    except IndexError:
        contact = 'none@example.com'

    return render(request, 'opensearch.xml', {
                 'opensearchbaseurl': "http://%s" % fqdn,
                 'fqdn': fqdn,
                 'contact': contact,
             }, mimetype = 'application/opensearchdescription+xml')

def suggest(request):
    '''
    opensearch suggestions view. Returns JSON

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding JSON
    '''

    if u'q' in request.GET:
        key = request.GET['q']
    else:
        key = None

    results = list(functions.search(key).values_list('serial', flat=True))
    # Simple JSON does not handle querysets so we cast to list
    results = list(results)
    response = simplejson.dumps([ key, results ])
    return HttpResponse(response, mimetype = 'application/x-suggestions+json')
