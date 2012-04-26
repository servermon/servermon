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
    help = "Loads a specific csv to equipment licenses"
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


        licenses = []

        with open(csvname, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                (foo, license, serial) = row
                licenses.append(license)

        for eq in Equipment.objects.exclude(model__name="DS2600"):
            mgmt = eq.servermanagement
            mgmt.license = licenses.pop()
            mgmt.save()
            print "OK: %s" % eq.serial

        print "OK; %s left" % len(licenses)
