# vim: ts=4 sts=4 et ai sw=4 fileencoding=utf-8

from servermon.hwdoc.models import Equipment, ServerManagement
from django.db.models import Q
from django.template import RequestContext
from django.shortcuts import render_to_response

def __search(key):
    if key is None:
        return None
    if key.upper().replace('R','').replace('U','').isdigit():
        rackunit = key.upper().replace('R','').replace('U','')
        if len(rackunit) < 3:
            result=Equipment.objects.filter(
                                        Q(rack=rackunit)|
                                        Q(unit=rackunit)
                                        )
        else:
            result=Equipment.objects.filter(rack=rackunit[0:2], unit=rackunit[2:4])
    else:
        result=Equipment.objects.filter(
                                        Q(serial=key)|
                                        Q(servermanagement__mac__icontains=key)|
                                        Q(servermanagement__hostname__icontains=key)
                                        )
    return result

def search(request):
    if u'key' in request.GET:
        key = request.GET['key']
    else:
        key = None

    return render_to_response('search.txt',
            { 'results': __search(key), },
            mimetype='text/plain',
            context_instance=RequestContext(request))
