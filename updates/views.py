from django.http import HttpResponse
from models import *

def index(request):
    hoststanza = ""
    for host in Host.objects.all():
        hoststanza += "<li><a href=\"%s\">%s</a>: %d updates</li>" % (host.hostname,host.hostname, Update.objects.filter(host=host).count())

    html = "<html><body><ul>%s</ul></body></html>" % hoststanza
    return HttpResponse(html)
        
    
def host(request,hostname):
    host = Host.objects.filter(hostname=hostname)[0]
    
    updatestanza = ""
    for update in host.update_set.all():
        updatestanza += "<li>%s: %s -> %s" % (update.package.name, update.installedVersion, update.candidateVersion)
    html = "<html><body><ul>%s</ul></body></html>" % updatestanza
    return HttpResponse(html)
        
