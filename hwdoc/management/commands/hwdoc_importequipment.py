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

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from hwdoc.models import Model, Equipment, ServerManagement
import sys
import csv
import re

class Command(BaseCommand):
    help = "Loads a specific csv to hwdoc Model, Equipment and ServerManagement models"
    args = "<file>"
    label = "file name to be imported"

    def handle(self, *args, **options):
        if args is None or len(args) != 1:
            raise CommandError("You must supply a file name")
        try:
            csvname = sys.argv[2]
        except IndexError:
            print "Error in usage. See help"
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
                else:
                    continue

                if len(dns) != 29 and eq != 'DS':
                    print "ERROR: Row: %s has wrong ILODNS row" % (row)
                    continue

                rack = rack.split('_')[1]
                unit = unit.split('-')[0][1:]

                e = Equipment()
                if eq == 'VMC':
                    e.model = Model.objects.get(name="DL385 G7")
                    e.purpose = eq
                elif eq == 'SC':
                    e.model = Model.objects.get(name="DL380 G7")
                    e.purpose = eq
                elif eq == 'DS':
                    e.model = Model.objects.get(name="DS2600")
                    e.purpose = eq

                e.serial = sn
                e.rack = rack
                e.unit = unit
                e.save()

                if eq == 'VMC' or eq == 'SC':
                    s = ServerManagement()
                    s.equipment = e
                    s.method = "ilo3"
                    s.hostname = dns
                    s.username = "Administrator"
                    s.password = passwd
                    s.mac = mac
                    s.save()

                print "OK: %s %s" % (eq, sn)
                count +=1
            print "Total " + str(count)
