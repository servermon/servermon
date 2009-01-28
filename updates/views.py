from django.http import HttpResponse
from django.shortcuts import render_to_response
from models import *
import ldap

def hostlist(request):
    return render_to_response('hostlist.html', {'hosts': Host.objects.order_by('hostname')})

def packagelist(request):
    return render_to_response('packagelist.html', {'packages': Package.objects.order_by('name')})
        
    
def host(request,hostname):
    host = Host.objects.filter(hostname=hostname)[0]
    ds = ldap.initialize("ldap://" + settings.LDAP_HOST)
    results = ds.search_s(settings.LDAP_BASE,ldap.SCOPE_SUBTREE,"(cn=%s)" % host.hostname)
    del ds
    ldapinfo = results[0][1]
    ipaddrs = ", ".join(ldapinfo['ipHostNumber'])
    puppetclasses = ", ".join(ldapinfo['puppetclass'])
    updates = host.update_set.order_by('package__name')
    return render_to_response('hostview.html', {'host': host, 'puppetclasses': puppetclasses, 'ipaddrs': ipaddrs, 'updates': updates})

def package(request,packagename):
    package = Package.objects.filter(name=packagename)[0]
    updates = package.update_set.order_by('host__hostname')
    return render_to_response('packageview.html', {'package': package, 'updates': updates})
