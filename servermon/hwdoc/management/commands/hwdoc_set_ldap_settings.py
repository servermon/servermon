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
Django management command to set LDAP BMC settings
'''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _
from django.utils.translation import ugettext_lazy as _l

from optparse import make_option

import _bmc_common

class Command(BaseCommand):
    '''
    Django management command to set LDAP BMC settings
    '''
    help = _l('Sets LDAP settings for BMC authentication')
    args = '[key]'

    option_list = BaseCommand.option_list + (
                make_option('--ldap_enable', action='store', dest='ldap_enable', help=_l('Enable LDAP authentication. Valid values: Yes, No')),
                make_option('--local_users_enable', action='store', dest='local_users_enable', help=_l('Enable/disable local users')),
                make_option('--ldap_server', action='store', dest='ldap_server', help=_l('LDAP server')),
                make_option('--lom_dn', action='store', dest='lom_dn', help=_l('iLO3 HP extended schema object dn')),
                make_option('--lom_password', action='store', dest='lom_password', help=_l('iLO3 HP extended schema object dn password')),
                make_option('--ldap_group_enable', action='store', dest='ldap_group_enable', help=_l('Enable/disable ldap groups')),
                make_option('--kerberos_realm', action='store', dest='kerberos_realm', help=_l('Kerberos realm. iLO3 support only')),
                make_option('--kdc_ip', action='store', dest='kdc_ip', help=_l('KDC Kerberos IP. iLO3 support only')),
                make_option('--kdc_port', action='store', dest='kdc_port', help=_l('KDC Kerberos port. iLO3 support only')),

                make_option('--contexts', action='store', dest='contexts', default=None, help=_l('List of comma separated contexts')),
                make_option('--groupnames', action='store', dest='groupnames', default=None, help=_l('LDAP group names')),
                make_option('--groupprivs', action='store', dest='groupprivs', default=None, help=_l('LDAP group privileges. iLO3 support only')),
                make_option('--groupsids', action='store', dest='groupsids', default=None, help=_l('LDAP group AD SIDs. iLO3 support only')),
            ) + _bmc_common.option_list

    def handle(self, *args, **options):
        '''
        Handle command
        '''

        options['command'] = 'set_ldap_settings'

        for s in options.keys():
            if s == 'contexts' and options['contexts'] is not None:
                options['contexts'] = options['contexts'].split(':')
            if s == 'groupnames' and options['groupnames'] is not None:
                options['groupnames'] = options['groupnames'].split(':')
            if s == 'groupprivs' and options['groupprivs'] is not None:
                options['groupprivs'] = options['groupprivs'].split(':')
            if s == 'groupsids' and options['groupsids'] is not None:
                options['groupsids'] = options['groupsids'].split(':')
        result = _bmc_common.handle(self, *args, **options)
