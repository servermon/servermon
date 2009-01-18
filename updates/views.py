from django.http import HttpResponse
from models import *

def index(request):
    hoststanza = ""
    updatestanza = ""
    for host in Host.objects.all():
        updates = Update.objects.filter(host=host)
        for update in updates:
            updatestanza += "<li>%s: %s -> %s</li>" % (update.package.name, update.installedVersion, update.candidateVersion)
        
        hoststanza += "<li><strong>%s</stong>: %d updates<ul>%s</ul></li>" % (host.hostname,len(updates),updatestanza)
    html = "<html><body><ul>%s</ul></body></html>" % hoststanza
    return HttpResponse(html)
        
    
