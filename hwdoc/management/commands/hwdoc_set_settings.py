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
Django management command to set BMC settings
'''

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from hwdoc.models import ServerManagement
from hwdoc.functions import search

import sys
import csv
import re
from optparse import make_option

class Command(BaseCommand):
    '''
    Django management command to set BMC settings
    '''
    help = 'Sets BMC settings. Sane defaults are assumed for all options. \
             Non applicable values for a backend are silently ignored'
    args = '[key]'
    label = search.__doc__

    option_list = BaseCommand.option_list + (
                # Yeah i know line length is violated here.
                make_option('--session_timeout', action='store', type='string', dest='session_timeout', help='BMC session timeout. Valid values: Backend dependent. iLO3 backend support only'),
                make_option('--ilo_enabled', action='store', type='string', dest='ilo_enabled', help='iLO status. Valid values: Y,N. iLO3 backend support only'),
                make_option('--f8_prompt_enabled', action='store', type='string', dest='f8_prompt_enabled', help='F8 on boot displayed. Valid values: Y,N. iLO3 backend support only'),
                make_option('--f8_login_required', action='store', type='string', dest='f8_login_required', help='Require Login for iLO BMC. Valid values: Y,N. iLO3 backend support only'),
                make_option('--https_port', action='store', type='string', dest='https_port', help='HTTPS Port. Valid values: 1-65535. iLO3 backend support only'),
                make_option('--http_port', action='store', type='string', dest='http_port', help='HTTP Port. Valid values: 1-65535. iLO3 backend support only'),
                make_option('--remote_console_port', action='store', type='string', dest='remote_console_port', help='Remote console port. Valid values: 1-65535. iLO3 backend support only'),
                make_option('--virtual_media_port', action='store', type='string', dest='virtual_media_port', help='Virtual media port. Valid values: 1-65535. iLO3 backend support only'),
                make_option('--ssh_port', action='store', type='string', dest='ssh_port', help='SSH Port. Valid values: 1-65535. iLO3 backend support only'),
                make_option('--ssh_status', action='store', type='string', dest='ssh_status', help='BMC SSH status. Valid values: Y,N. iLO3 backend support only'),
                make_option('--serial_cli_status', action='store', type='string', dest='serial_cli_status', help='Whether serial BMC redirection is enabled. Valid values: Y,N'),
                make_option('--serial_cli_speed', action='store', type='string', dest='serial_cli_speed', help='Speed of serial BMC redirection. Valid values: 9600,19200,38400,57600,115200'),
                make_option('--min_password', action='store', type='string', dest='min_password', help='Min password length. Valid values: Integer. Backend dependent?. iLO3 backend support only'),
                make_option('--auth_fail_logging', action='store', type='string', dest='auth_fail_logging', help='Authentication failure logging. Valid values: 0,1,2,3,5. iLO3 backend support only'),
                make_option('--rbsu_post_ip', action='store', type='string', dest='rbsu_post_ip', help='Show BMC IP during POST. Valid values: Y,N. iLO3 backend support only'),
                make_option('--enforce_aes', action='store', type='string', dest='enforce_aes', help='Set AES encyption in BMC. Valid values: Y,N. iLO3 backend support only'),
                make_option('-u', '--username',
                    action='store',
                    type='string',
                    dest='username',
                    default=None,
                    help='Provide username used to login to BMC'),
                make_option('-p', '--password',
                    action='store',
                    type='string',
                    dest='password',
                    default=None,
                    help='Provide password used to login to BMC'),
            )

    def handle(self, *args, **options):
        '''
        Handle command
        '''

        if args is None or len(args) != 1:
            raise CommandError("You must supply a key")

        try:
            key = args[0]
        except IndexError:
            print "Error in usage. See help"
            sys.exit(1)

        es = search(key)
        if es.count() == 0:
            print "No Equipment found"
            return

        for e in es:
            try:
                e.servermanagement
            except ServerManagement.DoesNotExist: 
                continue
            if int(options['verbosity']) > 0:
                print e
            set_options = options.copy()
            set_options.pop('username')
            set_options.pop('password')
            for s in set_options.keys():
                if set_options[s] is None:
                    set_options.pop(s)
            result = e.servermanagement.set_settings(options['username'], options['password'], **set_options)
            #TODO: Figure out what to do with this
            if int(options['verbosity']) > 1:
                print result
