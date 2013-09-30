# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
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
'''
Django management command to import a CSV
'''

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from hwdoc.models import EquipmentModel, Equipment, ServerManagement, Rack
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l
import sys
import csv
import re

class Command(BaseCommand):
    '''
    Django management command to import a CSV
    '''
    help = _l('Loads a specific CSV to hwdoc EquipmentModel, Equipment and ServerManagement models')
    args = '<file>'
    label = _l('file name to be imported')

    def handle(self, *args, **options):
        '''
        Handle command
        '''

        if args is None or len(args) != 1:
            raise CommandError(_('You must supply a file name'))
        try:
            csvname = sys.argv[2]
        except IndexError:
            print _('Error in usage. See help')
            sys.exit(1)

        count = 0
        with open(csvname, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                (aa, eq, sn, dns, passwd, rack, unit, pdua, pdub, mac) = row[:10]

                if eq.startswith('VMC'):
                    eq = 'VMC'
                elif re.match('^SC.-DS.$', eq):
                    eq = 'DS'
                elif eq.startswith('SC'):
                    eq = 'SC'
                elif eq.startswith('HN'):
                    eq = 'HN'
                else:
                    continue

                try:
                    rack = Rack.objects.get(pk=rack.split('_')[1])
                except Rack.DoesNotExist:
                    raise RuntimeError(_('The Rack %(rack)s you specified does not exist. You should create it first' % { 'rack': rack}))

                unit = unit.split('-')[0][1:]

                e = Equipment()
                if eq == 'VMC':
                    e.model = EquipmentModel.objects.get(name="DL385 G7")
                    e.purpose = eq
                elif eq == 'SC':
                    e.model = EquipmentModel.objects.get(name="DL380 G7")
                    e.purpose = eq
                elif eq == 'DS':
                    e.model = EquipmentModel.objects.get(name="DS2600")
                    e.purpose = eq
                elif eq == 'HN':
                    e.model = EquipmentModel.objects.get(name="PRIMERGY RX200 S5")
                    e.purpose = eq

                e.serial = sn
                e.rack = rack
                e.unit = unit
                e.save()

                if eq == 'VMC' or eq == 'SC' or eq == 'HN':
                    s = ServerManagement()
                    s.equipment = e
                    if eq == 'HN':
                        s.method = "irmc"
                        s.username = "admin"
                    elif eq == 'VMC' or eq == 'SC':
                        s.method = "ilo3"
                        s.username = "Administrator"
                    s.hostname = dns
                    s.password = passwd
                    s.mac = mac
                    s.save()

                print _('OK: %(eq)s %(sn)s') % { 'eq': eq, 'sn': sn)
                count +=1
            print _('Total ') + str(count)
