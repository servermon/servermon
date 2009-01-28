from django.db import models

class Host(models.Model):
    hostname = models.CharField(max_length=200)
    sshkey = models.CharField(max_length=500,blank=True)
    description = models.CharField(max_length=200)
    lastvisited = models.DateTimeField(auto_now=True)

    class Meta:
	ordering = ('hostname',)

    def __unicode__(self):
        if self.description:
            return "%s (%s)" % (self.hostname, self.description)
        else:
            return self.hostname

    def lastvisit(self):
        return self.lastvisited.strftime("%d/%m/%Y - %H:%M")

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
        return "%s@%s: %s -> %s" % (self.package.name, self.host.hostname, self.installedVersion, self.candidateVersion)
        
