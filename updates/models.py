from django.db import models
from servermon.puppet.models import Host
import re

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

    def get_changelog_url(self):
        return "http://packages.debian.org/changelogs/pool/main/%(initial)s/%(source)s/%(source)s_%(version)s/changelog#versionversion%(slug)s" % {'initial': self.package.sourcename[0], 'source': self.package.sourcename, 'version': re.sub(r'[0-9]+:', '', self.candidateVersion), 'slug': self.candidateVersion.replace('+','_') }
