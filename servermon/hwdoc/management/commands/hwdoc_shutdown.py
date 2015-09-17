# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2010-2012 Greek Research and Technology Network (GRNET S.A.)
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
Django management command to shutdown equipment
'''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from optparse import make_option

import _bmc_common


class Command(BaseCommand):
    '''
    Django management command to shutdown equipment
    '''
    help = _l('Shuts down equipment')
    args = '[key]'

    option_list = BaseCommand.option_list + (
        make_option('--force',
                    action='store_true',
                    dest='force',
                    default=False,
                    help=_('Force shutdown instead of sending an ACPI power off signal')),
    ) + _bmc_common.option_list

    def handle(self, *args, **options):
        '''
        Handle command
        '''

        if options['force']:
            options['command'] = 'power_off'
        else:
            options['command'] = 'power_off_acpi'

        _bmc_common.handle(self, *args, **options)
