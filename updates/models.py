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

from django.db import models
from servermon.puppet.models import Host
import re

class Package(models.Model):
    name = models.CharField(max_length=200)
    sourcename = models.CharField(max_length=200)
    hosts = models.ManyToManyField(Host, through='Update')
    
    class Meta:
        ordering = ('name', )

    def __unicode__(self):
        if self.name == self.sourcename:
            return self.name
        else:
            return "%s (%s)" % (self.name, self.sourcename)

class Update(models.Model):
    package = models.ForeignKey(Package)
    host = models.ForeignKey(Host)
    installedVersion = models.CharField(max_length=200)
    candidateVersion = models.CharField(max_length=200)
    source = models.CharField(max_length=200)
    origin = models.CharField(max_length=200, null=True)
    is_security = models.BooleanField(default=False)

    def __unicode__(self):
        return "%s@%s: %s -> %s" % (self.package.name, self.host.name, self.installedVersion, self.candidateVersion)

    def get_changelog_url(self):
        if self.origin == 'Debian':
            url = "http://packages.debian.org/changelogs/pool/main/%(initial)s/%(source)s/%(source)s_%(version)s/changelog#versionversion%(slug)s"
        elif self.origin == 'Ubuntu':
            url = "http://changelogs.ubuntu.com/changelogs/pool/main/%(initial)s/%(source)s/%(source)s_%(version)s/changelog#versionversion%(slug)s"
        else:
            return None

        return url % {
            'initial': self.package.sourcename[0],
            'source': self.package.sourcename,
            'version': re.sub(r'[0-9]+:', '', self.candidateVersion),
            'slug': self.candidateVersion.replace('+','_')
        }
