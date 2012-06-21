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
Django management command to set LDAP BMC settings
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
    Django management command to set LDAP BMC settings
    '''
    help = 'Sets LDAP settings for BMC authentication'
    args = '[key]'
    label = search.__doc__

    option_list = BaseCommand.option_list + (
                make_option('--ldap_enable', action='store', dest='ldap_enable', help='Enable LDAP authentication. Valid values: Yes,No'),
                make_option('--local_users_enable', action='store', dest='local_users_enable', help='Enable/disable local users'),
                make_option('--ldap_server', action='store', dest='ldap_server', help='LDAP server'),
                make_option('--lom_dn', action='store', dest='lom_dn', help='iLO3 HP extended schema object dn'),
                make_option('--lom_password', action='store', dest='lom_password', help='iLO3 HP extended schema object dn password'),
                make_option('--ldap_group_enable', action='store', dest='ldap_group_enable', help='Enable/disable ldap groups'),
                make_option('--kerberos_realm', action='store', dest='kerberos_realm', help='Kerberos realm. iLO3 support only'),
                make_option('--kdc_ip', action='store', dest='kdc_ip', help='KDC Kerberos IP. iLO3 support only'),
                make_option('--kdc_port', action='store', dest='kdc_port', help='KDC Kerberos port. iLO3 support only'),

                make_option('--contexts', action='store', dest='contexts', default=None, help='List of comma separated contexts'),
                make_option('--groupnames', action='store', dest='groupnames', default=None, help='LDAP group names'),
                make_option('--groupprivs', action='store', dest='groupprivs', default=None, help='LDAP group privileges. iLO3 support only'),
                make_option('--groupsids', action='store', dest='groupsids', default=None, help='LDAP group AD SIDs. iLO3 support only'),

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
            ldap_opts = options.copy()
            ldap_opts.pop('username')
            ldap_opts.pop('password')
            for s in ldap_opts.keys():
                if s == 'contexts' and ldap_opts['contexts'] is not None:
                    ldap_opts['contexts'] = ldap_opts['contexts'].split(':')
                if s == 'groupnames' and ldap_opts['groupnames'] is not None:
                    ldap_opts['groupnames'] = ldap_opts['groupnames'].split(':')
                if s == 'groupprivs' and ldap_opts['groupprivs'] is not None:
                    ldap_opts['groupprivs'] = ldap_opts['groupprivs'].split(':')
                if s == 'groupsids' and ldap_opts['groupsids'] is not None:
                    ldap_opts['groupsids'] = ldap_opts['groupsids'].split(':')
                if ldap_opts[s] is None:
                    ldap_opts.pop(s)

            result = e.servermanagement.set_ldap_settings(options['username'], options['password'], **ldap_opts)
            #TODO: Figure out what to do with this
            if int(options['verbosity']) > 1:
                print result
