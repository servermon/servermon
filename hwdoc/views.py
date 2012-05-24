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

from hwdoc.models import Project, Model, Equipment, ServerManagement
from django.db.models import Q
from hwdoc import functions
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.conf import settings
from django.contrib.sites.models import Site

def index(request):
    racks = Equipment.objects.order_by('rack').values_list('rack', flat=True).distinct()
    projects = Project.objects.order_by('name').all()
    models = Model.objects.order_by('vendor__name','name').all()
    
    return render_to_response('hwdocindex.html',
            {   'racks': racks,
                'projects': projects,
                'models': models,
            },
            context_instance=RequestContext(request))

def equipment(request, equipment_id):
    template = 'equipment.html'

    equipment = get_object_or_404(Equipment,pk=equipment_id)
    return render_to_response(template,
            { 'equipment': equipment, },
            context_instance=RequestContext(request))

def project(request, project_id):
    template = 'project.html'

    project = get_object_or_404(Project,pk=project_id)
    return render_to_response(template,
            { 'project': project, },
            context_instance=RequestContext(request))

def search(request):
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

    return render_to_response(template,
            { 'results': functions.search(key), },
            mimetype=mimetype,
            context_instance=RequestContext(request))

def advancedsearch(request):
    return render_to_response('advancedsearch.html',
            context_instance=RequestContext(request))

def opensearch(request):
    fqdn = Site.objects.get_current().domain
    try:
        contact = settings.ADMINS[0][0]
    except IndexError:
        contact = 'none@example.com'

    return render_to_response('opensearch.xml',
             {
                 'opensearchbaseurl': "http://%s" % fqdn,
                 'fqdn': fqdn,
                 'contact': contact,
                 },
             context_instance=RequestContext(request),
             mimetype = 'application/opensearchdescription+xml'
            )

