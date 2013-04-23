# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
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

from servermon.puppet import functions as puppet_functions
from servermon.hwdoc import functions as hwdoc_functions
from servermon.projectwide import functions as projectwide_functions
from servermon.puppet.models import Host, Fact, FactValue
from servermon.updates.models import Package
from servermon.compat import render
from django.core.exceptions import FieldError
from django.http import HttpResponse
from django.contrib.sites.models import Site
from django.utils import simplejson
from django.db.models import Count
from django.db import DatabaseError
from django.template import TemplateSyntaxError
from datetime import datetime, timedelta
from settings import HOST_TIMEOUT, ADMINS
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

    return render(request, "index.html", {
        'problemhosts': problemhosts, 
        'timeout': timeout,
        'hosts': hosts,
        'factcount': factcount,
        'factvaluecount': factvaluecount,
        'updatecount': updatecount,
        'packagecount': packagecount,
        'securitycount': securitycount,
        })

def search(request):
    '''
    Search view. Scans request for q (GET case) or qarea (POST case) and
    searches for corresponding instances in all subapps matching the query
    If txt is send in a GET it will display results in txt and not in html
    format

    @type   request: HTTPRequest 
    @param  request: Django HTTPRequest object
    @rtype: HTTPResponse
    @return: HTTPResponse object rendering corresponding HTML
    '''

    if u'txt' in request.GET:
        template = 'results.txt'
        content_type = 'text/plain'
    else:
        template = 'results.html'
        content_type = 'text/html'

    if u'q' in request.GET:
        key = request.GET['q']
    elif u'qarea' in request.POST:
        key = projectwide_functions.get_search_terms(request.POST['qarea']) 
    else:
        key = None

    results = {
        'hwdoc': None,
        'puppet': None,
        'updates': None,
        }

    results['puppet'] = puppet_functions.search(key).select_related()
    results['hwdoc'] = hwdoc_functions.search(key).select_related(
                        'servermanagement', 'rack', 'model',
                        'model__vendor', 'allocation')

    results['hwdoc'] = hwdoc_functions.populate_tickets(results['hwdoc'])
    results['hwdoc'] = hwdoc_functions.populate_hostnames(results['hwdoc'])

    try:
        return render(request, template,
                    { 'results': results, },
                    content_type=content_type)
    except TemplateSyntaxError as e:
        if re.search('too many SQL variables', e.message):
            return render(request, 'error.html', content_type=content_type)

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
        contact = ADMINS[0][0]
    except IndexError:
        contact = 'none@example.com'

    return render(request, 'opensearch.xml', {
                 'opensearchbaseurl': "http://%s" % fqdn,
                 'fqdn': fqdn,
                 'contact': contact,
             }, content_type = 'application/opensearchdescription+xml')

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

    results = {
        'hwdoc': None,
        'puppet': None,
        'updates': None,
        }

    results['puppet'] = puppet_functions.search(key).annotate(Count('value'))
    results['hwdoc'] = hwdoc_functions.search(key).annotate(Count('serial'))
    
    try:
        response = simplejson.dumps([ key,
            list(results['hwdoc'].values_list('serial', flat=True)) +
            list(results['puppet'].values_list('value', flat=True)),
            list(results['hwdoc'].values_list('serial__count', flat=True)) + 
            list(results['puppet'].values_list('value__count', flat=True)),
            ]
            )
    except (DatabaseError, FieldError):
        response = simplejson.dumps([ key, ])

    return HttpResponse(response, mimetype = 'application/x-suggestions+json')
