# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
# Copyright © 2014 Alexandros Kosiaris
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHORS DISCLAIMS ALL WARRANTIES WITH REGARD
# TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS. IN NO EVENT SHALL THE AUTHORS BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT,
# OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF
# USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER
# TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE
# OF THIS SOFTWARE.
'''
Django management command to populate updatable packages in DB
'''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _l

from xml.dom.minidom import parseString
from updates.models import Package, Update
from django.db import transaction

from puppet.models import Host


class Command(BaseCommand):
    '''
    Django management command to populate updatable packages in DB
    '''
    help = _l('Populate updatable packages in DB')

    @transaction.commit_on_success
    def handle(self, *args, **options):
        '''
        Handle command
        '''
        for host in Host.objects.all():
            self.gen_host_updates(host)

        Package.objects.filter(hosts__isnull=True).delete()

    def gen_host_updates(self, host):
        '''
        Populate all updates
        '''

        # First let's delete them all
        host.update_set.all().delete()

        try:
            xml = parseString(host.get_fact_value('package_updates'))
        except:
            return

        for update in xml.getElementsByTagName("package"):
            name = update.getAttribute("name")
            cv = update.getAttribute("current_version")
            nv = update.getAttribute("new_version")
            sn = update.getAttribute("source_name")
            org = update.getAttribute("origin")
            # Note: facts are forcefully stringified until puppet 3.7
            is_sec = (update.getAttribute("is_security") == "true")

            try:
                p = Package.objects.get(name=name)
            except Package.DoesNotExist:
                p = Package(name=name, sourcename=sn)
                p.save()

            u = Update(host=host, package=p,
                       installedVersion=cv, candidateVersion=nv,
                       origin=org,
                       is_security=is_sec)

            u.save()
