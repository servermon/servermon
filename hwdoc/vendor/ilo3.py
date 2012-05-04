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
import socket
import pprint

def power_on(hostname, username, password):
    return __send__(hostname, username, password, __power_on_command__())

def power_off(hostname, username, password):
    return __send__(hostname, username, password, __power_off_command__())

def power_off_acpi(hostname, username, password):
    return __send__(hostname, username, password, __power_off_acpi_command__())

def power_cycle(hostname, username, password):
    return __send__(hostname, username, password, __power_cycle_command__())

def power_reset(hostname, username, password):
    return __send__(hostname, username, password, __power_reset_command__())

def pass_change(hostname, username, password, **kwargs):
    if 'change_username' not in kwargs or 'newpass' not in kwargs:
        raise RuntimeError('Username and/or password to changed not given')
    return __send__(hostname, username, password, __pass_change_command__(
        kwargs['change_username'], kwargs['newpass']))

def set_settings(hostname, username, password, **kwargs):
    return __send__(hostname, username, password, __mod_global_settings__(**kwargs))

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
    except (httplib2.ServerNotFoundError, socket.error) as e:
        # TODO: Log this. For now just print
        print e
        return
    return content

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

def __pass_change_command__(username, newpass):
    command = '''
    <USER_INFO MODE="write">
        <MOD_USER USER_LOGIN="%s">
            <PASSWORD value="%s"/>
        </MOD_USER>
    </USER_INFO>
    ''' % (username, newpass)
    return command.strip()

def __mod_global_settings__(**kwargs):
    kwargs.setdefault('session_timeout','30')
    kwargs.setdefault('ilo_enabled','Y')
    kwargs.setdefault('f8_prompt_enabled','Y')
    kwargs.setdefault('f8_login_required','N')
    kwargs.setdefault('https_port','443')
    kwargs.setdefault('http_port','80')
    kwargs.setdefault('remote_console_port','17990')
    kwargs.setdefault('virtual_media_port','17988')
    kwargs.setdefault('ssh_port','22')
    kwargs.setdefault('ssh_status','Y')
    kwargs.setdefault('serial_cli_status','3')
    kwargs.setdefault('serial_cli_speed','5')
    kwargs.setdefault('min_password','8')
    kwargs.setdefault('auth_fail_logging','3')
    kwargs.setdefault('rbsu_post_ip','Y')
    kwargs.setdefault('enforce_aes','N')
    kwargs.setdefault('high_perf_mouse','No')

    command = '''
<RIB_INFO mode="write">
    <MOD_GLOBAL_SETTINGS>
        <SESSION_TIMEOUT VALUE="%(session_timeout)s"/>
        <ILO_FUNCT_ENABLED VALUE="%(ilo_enabled)s"/>
        <F8_PROMPT_ENABLED VALUE="%(f8_prompt_enabled)s"/>
        <F8_LOGIN_REQUIRED VALUE="%(f8_login_required)s"/>
        <HTTPS_PORT VALUE="%(https_port)s"/>
        <HTTP_PORT VALUE="%(http_port)s"/>
        <REMOTE_CONSOLE_PORT VALUE="%(remote_console_port)s"/>
        <VIRTUAL_MEDIA_PORT VALUE="%(virtual_media_port)s"/>
        <SSH_PORT VALUE="%(ssh_port)s"/>
        <SSH_STATUS VALUE="%(ssh_status)s"/>
        <SERIAL_CLI_STATUS VALUE="%(serial_cli_status)s"/>
        <SERIAL_CLI_SPEED VALUE="%(serial_cli_speed)s"/>
        <MIN_PASSWORD VALUE="%(min_password)s"/>
        <AUTHENTICATION_FAILURE_LOGGING VALUE="%(auth_fail_logging)s"/>
        <RBSU_POST_IP VALUE="%(rbsu_post_ip)s"/>
        <ENFORCE_AES VALUE="%(enforce_aes)s"/>
        <HIGH_PERFORMANCE_MOUSE value="%(high_perf_mouse)s" />
    </MOD_GLOBAL_SETTINGS>
</RIB_INFO>
    ''' % kwargs
    print command
    return command

# TODO: Implement these too and figure out differences
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

