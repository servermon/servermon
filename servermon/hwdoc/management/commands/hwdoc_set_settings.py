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
Django management command to set BMC settings
'''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _l

from optparse import make_option

import _bmc_common


class Command(BaseCommand):
    '''
    Django management command to set BMC settings
    '''
    help = _l('Sets BMC settings. Sane defaults are assumed for all options. \
             Non applicable values for a backend are silently ignored')
    args = '[key]'

    option_list = BaseCommand.option_list + (
        # Yeah i know line length is violated here.
        make_option('--session_timeout', action='store', type='string', dest='session_timeout', help=_l('BMC session timeout. Valid values: Backend dependent. iLO3 backend support only')),
        make_option('--ilo_enabled', action='store', type='string', dest='ilo_enabled', help=_l('iLO status. Valid values: Y,N. iLO3 backend support only')),
        make_option('--f8_prompt_enabled', action='store', type='string', dest='f8_prompt_enabled', help=_l('F8 on boot displayed. Valid values: Y,N. iLO3 backend support only')),
        make_option('--f8_login_required', action='store', type='string', dest='f8_login_required', help=_l('Require Login for iLO BMC. Valid values: Y,N. iLO3 backend support only')),
        make_option('--https_port', action='store', type='string', dest='https_port', help=_l('HTTPS Port. Valid values: 1-65535. iLO3 backend support only')),
        make_option('--http_port', action='store', type='string', dest='http_port', help=_l('HTTP Port. Valid values: 1-65535. iLO3 backend support only')),
        make_option('--remote_console_port', action='store', type='string', dest='remote_console_port', help=_l('Remote console port. Valid values: 1-65535. iLO3 backend support only')),
        make_option('--virtual_media_port', action='store', type='string', dest='virtual_media_port', help=_l('Virtual media port. Valid values: 1-65535. iLO3 backend support only')),
        make_option('--ssh_port', action='store', type='string', dest='ssh_port', help=_l('SSH Port. Valid values: 1-65535. iLO3 backend support only')),
        make_option('--ssh_status', action='store', type='string', dest='ssh_status', help=_l('BMC SSH status. Valid values: Y,N. iLO3 backend support only')),
        make_option('--serial_cli_status', action='store', type='string', dest='serial_cli_status', help=_l('Whether serial BMC redirection is enabled. Valid values: Y,N')),
        make_option('--serial_cli_speed', action='store', type='string', dest='serial_cli_speed', help=_l('Speed of serial BMC redirection. Valid values: 9600, 19200, 38400, 57600, 115200')),
        make_option('--min_password', action='store', type='string', dest='min_password', help=_l('Min password length. Valid values: Integer. Backend dependent?. iLO3 backend support only')),
        make_option('--auth_fail_logging', action='store', type='string', dest='auth_fail_logging', help=_l('Authentication failure logging. Valid values: 0,1,2,3,5. iLO3 backend support only')),
        make_option('--rbsu_post_ip', action='store', type='string', dest='rbsu_post_ip', help=_l('Show BMC IP during POST. Valid values: Y,N. iLO3 backend support only')),
        make_option('--enforce_aes', action='store', type='string', dest='enforce_aes', help=_l('Set AES encyption in BMC. Valid values: Y,N. iLO3 backend support only')),
    ) + _bmc_common.option_list

    def handle(self, *args, **options):
        '''
        Handle command
        '''

        options['command'] = 'set_settings'
        _bmc_common.handle(self, *args, **options)
