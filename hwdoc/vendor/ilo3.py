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

import httplib2
import pprint

def power_on(hostname, username, password):
    return __send__(hostname, username, password, __power_on_command__())

def power_off(hostname, username, password):
    return __send__(hostname, username, password, __power_off_command__())

def power_off_acpi(hostname, username, password):
    return __send__(hostname, username, password, __power_off_acpi_command__())

def power_cycle(hostname, username, password):
    return __send__(hostname, username, password, __power_on_command__())

def power_reset(hostname, username, password):
    return __send__(hostname, username, password, __power_on_command__())

def __send__(hostname, username, password, command):
    h = httplib2.Http(disable_ssl_certificate_validation=True)

    body = '''
    <RIBCL VERSION="2.0">
        <LOGIN USER_LOGIN="%s" PASSWORD="%s">%s</LOGIN>
    </RIBCL>''' % (username, password, command)

    body = str(body)

    try:
        resp, content = h.request(
                            'https://%s/ribcl' % str(hostname),
                            'POST',
                            body = body,
                            headers = { 'TE': 'chunked', 'Connection': 'close'}
                        )
    except httplib2.ServerNotFoundError as e:
        # TODO: Log this. For now just print
        print e
        return
    return (resp, content)

def __power_on_command__():
    command = '''
    <SERVER_INFO MODE="write">
        <SET_HOST_POWER HOST_POWER="Yes"/>
    </SERVER_INFO>
    '''
    return command.strip()

def __power_off_command__():
    command = '''
    <SERVER_INFO MODE="write">
        <HOLD_PWR_BTN TOGGLE="Yes"/>
    </SERVER_INFO>
    '''
    return command.strip()

def __power_off_acpi_command__():
    command = '''
    <SERVER_INFO MODE="write">
        <SET_HOST_POWER HOST_POWER="No"/>
    </SERVER_INFO>
    '''
    return command.strip()

def __power_cycle_command__():
    command = '''
    <SERVER_INFO MODE="write">
        <COLD_BOOT_SERVER/>
    </SERVER_INFO>
    '''
    return command.strip()

def __power_reset_command__():
    command = '''
    <SERVER_INFO MODE="write">
        <WARM_BOOT_SERVER/>
    </SERVER_INFO>
    '''
    return command.strip()

# TODO: Implement these too and figure out differences
def __password_change_command__(username, newpass):
    command = '''
    <USER_INFO MODE="write">
        <MOD_USER USER_LOGIN="%s">
            <PASSWORD value="%s"/>
        </MOD_USER>
    </USER_INFO>
    ''' % (username, newpass)
    return command.strip()

def __power_reset_command__():
    command = '''
    <SERVER_INFO MODE="write">
        <RESET_SERVER/>
    </SERVER_INFO>
    '''
    return command.strip()

def __reset_rib_command__():
    command = '''
    <RIB_INFO MODE="write">
        <RESET_RIB/>
    </RIB_INFO>
    '''
    return command.strip()

