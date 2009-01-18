from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=200)
    sshkey = models.CharField(max_length=500)
    description = models.CharField(max_length=200)

class Package(models.Model):
    name = models.CharField(max_length=200)
    hosts = models.ManyToManyField(Host, through='Update')

class Update(models.Model):
    package = models.ForeignKey(Package)
    host = models.ForeignKey(Host)
    installedVersion = models.CharField(max_length=200)
    candidateVersion = models.CharField(max_length=200)
    source = models.CharField(max_length=200)

    def __unicode__(self):
        return "%s@%s: %s -> %s" % (self.package.name, self.host.hostname, self.installedVersion, self.candidateVersion)
        
