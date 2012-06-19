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

from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.db.models import Count
from servermon.puppet.models import Host
from servermon.updates.models import Package

def hostlist(request):
    hosts = Host.objects.annotate(update_count=Count('update'))
    return render_to_response('hostlist.html', {'hosts': hosts })

def packagelist(request):
    packages = Package.objects.annotate(host_count=Count('hosts'))
    return render_to_response('packagelist.html', {'packages': packages })

def package(request,packagename):
    package = Package.objects.filter(name=packagename)[0]
    updates = package.update_set.order_by('host__name')
    if "plain" in request.GET:
        return render_to_response("package.txt", {"updates": updates}, mimetype="text/plain")
    return render_to_response('packageview.html', {'package': package, 'updates': updates})
