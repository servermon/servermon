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
Django management command to add user to BMC
'''

from django.core.management.base import BaseCommand
from hwdoc.functions import search
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from optparse import make_option

import _common

class Command(BaseCommand):
    '''
    Django management command to get all Users configured in the BMC
    '''
    help = _l('Get a list of all users configured in the BMC')
    args = '[key]'
    label = search.__doc__

    option_list = BaseCommand.option_list + _common.option_list

    def handle(self, *args, **options):
        '''
        Handle command
        '''

        options['command'] = 'get_all_users'
        result = _common.handle(self, *args, **options)
