from django.db import models
from puppet.models import Host

class Package(models.Model):
    name = models.CharField(max_length=200)
    sourcename = models.CharField(max_length=200)
    hosts = models.ManyToManyField(Host, through='Update')
    
    class Meta:
        ordering = ('name', )

class Update(models.Model):
    package = models.ForeignKey(Package)
    host = models.ForeignKey(Host)
    installedVersion = models.CharField(max_length=200)
    candidateVersion = models.CharField(max_length=200)
    source = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s@%s: %s -> %s" % (self.package.name, self.host.name, self.installedVersion, self.candidateVersion)
        
