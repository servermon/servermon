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
    return __send__(hostname, username, password, __mod_global_settings__(**kwargs) + __mod_network_settings__(**kwargs))

def boot_order(hostname, username, password, **kwargs):
    return __send__(hostname, username, password, __boot_order__(**kwargs))

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

def __mod_network_settings__(**kwargs):
    # TODO: This has not yet been exported to any django management command.
    # As a result only defaults are used, but are good enough for now.
    kwargs.setdefault('dhcp_enable', 'Yes')

    kwargs.setdefault('enable_nic', 'Yes')
    kwargs.setdefault('shared_network', 'N')
    kwargs.setdefault('vlan_enabled', 'N')
    kwargs.setdefault('vlan_id', '0')
    kwargs.setdefault('speed_auto', 'Y')
    kwargs.setdefault('nic_speed', '10')
    kwargs.setdefault('full_duplex', 'N')
    kwargs.setdefault('reg_wins', 'Y')
    kwargs.setdefault('reg_ddns', 'Y')
    kwargs.setdefault('ping_gateway', 'Y')
    kwargs.setdefault('timezone', 'Europe/Athens')
    kwargs.setdefault('static_route1_dest', '0.0.0.0')
    kwargs.setdefault('static_route1_mask', '0.0.0.0')
    kwargs.setdefault('static_route1_gw', '0.0.0.0')
    kwargs.setdefault('static_route2_dest', '0.0.0.0')
    kwargs.setdefault('static_route2_mask', '0.0.0.0')
    kwargs.setdefault('static_route2_gw', '0.0.0.0')
    kwargs.setdefault('static_route3_dest', '0.0.0.0')
    kwargs.setdefault('static_route3_mask', '0.0.0.0')
    kwargs.setdefault('static_route3_gw', '0.0.0.0')

    if 'dhcp_enable' in kwargs:
        kwargs.setdefault('dhcp_gateway', 'Yes')
        kwargs.setdefault('dhcp_dns', 'Yes')
        kwargs.setdefault('dhcp_wins', 'Yes')
        kwargs.setdefault('dhcp_static_route', 'Yes')
        kwargs.setdefault('dhcp_domain_name', 'Yes')
        kwargs.setdefault('dhcp_sntp', 'Yes')
        networksettings = '''
        <DHCP_ENABLE VALUE="%(dhcp_enable)s"/>
        <DHCP_GATEWAY VALUE="%(dhcp_gateway)s"/>
        <DHCP_DNS_SERVER VALUE="%(dhcp_dns)s"/>
        <DHCP_WINS_SERVER VALUE="%(dhcp_wins)s"/>
        <DHCP_STATIC_ROUTE VALUE="%(dhcp_static_route)s"/>
        <DHCP_DOMAIN_NAME VALUE="%(dhcp_domain_name)s"/>
        <DHCP_SNTP_SETTINGS VALUE="%(dhcp_sntp)s"/>
''' % kwargs
    else:
        kwargs.setdefault('ip_address', '10.0.0.2')
        kwargs.setdefault('subnet_mask', '255.255.255.0')
        kwargs.setdefault('gw_ip   ', '10.0.0.1')
        kwargs.setdefault('dns_name', 'demo')
        kwargs.setdefault('domain  ', 'example.com')
        kwargs.setdefault('dns_server1', '10.0.0.10')
        kwargs.setdefault('dns_server2', '10.0.0.20')
        kwargs.setdefault('dns_server3', '10.0.0.30')
        kwargs.setdefault('wins_server1', '10.0.0.40')
        kwargs.setdefault('wins_server2', '10.0.0.50')
        networksettings = '''
            <IP_ADDRESS value="%(ip_address)s"/>
            <SUBNET_MASK value="%(subnet_mask)s"/>
            <GATEWAY_IP_ADDRESS value="%(gw_ip)s"/>
            <DNS_NAME value="%(dns_name)s"/>
            <DOMAIN_NAME value="%(domain)s"/>
            <PRIM_DNS_SERVER value="%(dns_server1)s"/>
            <SEC_DNS_SERVER value="%(dns_server2)s"/>
            <TER_DNS_SERVER value="%(dns_server3)s"/>
            <PRIM_WINS_SERVER value="%(wins_server1)s"/>
            <SEC_WINS_SERVER value="%(wins_server2)s"/>
''' % kwargs

    othersettings = '''
        <ENABLE_NIC VALUE="%(enable_nic)s"/>
        <SHARED_NETWORK_PORT VALUE="%(shared_network)s"/>
        <VLAN_ENABLED VALUE="%(vlan_enabled)s"/>
        <VLAN_ID VALUE="%(vlan_id)s"/>
        <SPEED_AUTOSELECT VALUE="%(speed_auto)s"/>
        <NIC_SPEED VALUE="%(nic_speed)s"/>
        <FULL_DUPLEX VALUE="%(full_duplex)s"/>
        <REG_WINS_SERVER VALUE="%(reg_wins)s"/>
        <REG_DDNS_SERVER VALUE="%(reg_ddns)s"/>
        <PING_GATEWAY VALUE="%(ping_gateway)s"/>
        <TIMEZONE VALUE="%(timezone)s"/>
        <STATIC_ROUTE_1 DEST="%(static_route1_dest)s" MASK="%(static_route1_mask)s" GATEWAY="%(static_route1_gw)s"/>
        <STATIC_ROUTE_2 DEST="%(static_route2_dest)s" MASK="%(static_route2_mask)s" GATEWAY="%(static_route2_gw)s"/>
        <STATIC_ROUTE_3 DEST="%(static_route3_dest)s" MASK="%(static_route3_mask)s" GATEWAY="%(static_route3_gw)s"/>
    ''' % kwargs

    command = '''
<RIB_INFO mode="write">
    <MOD_NETWORK_SETTINGS>
    %s
    %s
    </MOD_NETWORK_SETTINGS>
</RIB_INFO>
    ''' % (networksettings, othersettings)
    return command


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
    return command

def __boot_order__(**kwargs):
    if kwargs['once']:
        command = '''
        <SERVER_INFO MODE="write">
            <SET_ONE_TIME_BOOT value = "%s" />
        </SERVER_INFO>
        ''' % kwargs['boot_list'][0]
    else:
        boot_list = ''
        for b in kwargs['boot_list']:
            boot_list = boot_list + '<DEVICE VALUE = "%s" />' % b
        command = '''
        <SERVER_INFO MODE="write">
            <SET_PERSISTENT_BOOT>
            %s
            </SET_PERSISTENT_BOOT>
        </SERVER_INFO>
        ''' % boot_list
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

