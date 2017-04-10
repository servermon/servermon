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
HP iLO3 implementation of hwdoc Django management commmands
'''

import httplib2
import socket


def power_on(hostname, username, password, **kwargs):
    '''
    Power on command
    '''
    return __send__(hostname, username, password, __power_on_command__())


def power_off(hostname, username, password, **kwargs):
    '''
    Power off command
    '''
    return __send__(hostname, username, password, __power_off_command__())


def power_off_acpi(hostname, username, password, **kwargs):
    '''
    Power off using ACPI command
    '''
    return __send__(hostname, username, password, __power_off_acpi_command__())


def power_cycle(hostname, username, password, **kwargs):
    '''
    Cold boot command
    '''
    return __send__(hostname, username, password, __power_cycle_command__())


def power_reset(hostname, username, password, **kwargs):
    '''
    Warm boot command
    '''
    return __send__(hostname, username, password, __power_reset_command__())


def pass_change(hostname, username, password, **kwargs):
    '''
    Change BMC password
    '''
    return __send__(
        hostname, username, password,
        __pass_change_command__(kwargs['change_username'], kwargs['newpass']))


def set_settings(hostname, username, password, **kwargs):
    '''
    Set BMC settings
    '''
    return __send__(
        hostname, username, password,
        __mod_global_settings_command__(**kwargs) +
        __mod_network_settings_command__(**kwargs) +
        __power_on_delay_command__(**kwargs))


def set_ldap_settings(hostname, username, password, **kwargs):
    '''
    Set BMC LDAP settings
    '''
    return __send__(
        hostname, username, password,
        __mod_directory_command__(**kwargs))


def boot_order(hostname, username, password, **kwargs):
    '''
    Set boot order
    '''
    return __send__(hostname, username, password, __boot_order_command__(**kwargs))


def license_set(hostname, username, password, **kwargs):
    '''
    Set BMC License
    '''
    return __send__(hostname, username, password, __license_set_command__(**kwargs))


def bmc_reset(hostname, username, password, **kwargs):
    '''
    Reset BMC
    '''
    return __send__(hostname, username, password, __reset_rib_command__())


def bmc_factory_defaults(hostname, username, password, **kwargs):
    '''
    Reset BMC to factory defaults
    '''
    return __send__(hostname, username, password, __factory_defaults_command__())


def add_user(hostname, username, password, **kwargs):
    '''
    Add a user to iLO
    '''
    return __send__(hostname, username, password, __add_user_command__(**kwargs))


def remove_user(hostname, username, password, **kwargs):
    '''
    Remove a user from iLO
    '''
    return __send__(hostname, username, password, __remove_user_command__(**kwargs))


def get_all_users(hostname, username, password, **kwargs):
    '''
    Get a list of all configured users to the iLO
    '''
    return __send__(hostname, username, password, __get_all_users_command__(**kwargs))


def firmware_update(hostname, username, password, **kwargs):
    '''
    Perform a firmware update of the iLO
    '''
    try:
        f = open(kwargs['firmware_location']).read()
    except IOError:
        # TODO: Log this
        print "Could not read firmware file"
        return False

    content_type, body = encode_multipart_formdata(
        (('fileType', ''), ),
        (('fwimgfile', kwargs['firmware_location'], f), ),
    )
    extras = {
        'Content-Type': content_type,
        'body': body,
    }

    try:
        extras = {'Cookie': extras['Cookie']}
    except IndexError:
        # TODO: Log this
        print "Failed to get Cookie from iLO"
        return False
    return __send__(hostname, username, password, __firmware_update_command__(**kwargs), extras)


# Beneath this line iLO3 specifics start
def __send__(hostname, username, password, command, extras=None):
    h = httplib2.Http(disable_ssl_certificate_validation=True)

    body = '''
    <RIBCL VERSION="2.0">
        <LOGIN USER_LOGIN="%s" PASSWORD="%s">%s</LOGIN>
    </RIBCL>''' % (username, password, command)

    body = str(body)
    headers = {
        'TE': 'chunked',
        'Connection': 'close',
    }
    url = 'https://%s/ribcl' % str(hostname)
    if extras is not None:
        if 'Content-Type' in extras.keys():
            headers.update({'Content-Type': extras['Content-Type']})
            body = str(extras['body'])
            url = 'https://%s/cgi-bin/uploadRibclFiles' % str(hostname)
        else:
            headers.update(extras)
    try:
        resp, content = h.request(
            url, 'POST', body=body, headers=headers)
    except (httplib2.ServerNotFoundError, socket.error) as e:
        # TODO: Log this. For now just print
        print e
        return
    if extras is not None and 'set-cookie' in resp:
        extras['Cookie'] = resp['set-cookie']
    return content


def encode_multipart_formdata(fields, files):
    '''
    fields is a sequence of (name, value) elements for regular form fields.
    files is a sequence of (name, filename, value) elements for data to be uploaded as files
    Return (content_type, body) ready for httplib.HTTP instance
    '''
    BOUNDARY = '----------bound@ry_$'
    CRLF = '\r\n'
    L = []
    for (key, value) in fields:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"' % key)
        L.append('')
        L.append(value)
    for (key, filename, value) in files:
        L.append('--' + BOUNDARY)
        L.append('Content-Disposition: form-data; name="%s"; filename="%s"' % (key, filename))
        L.append('Content-Type: %s' % ('application/octet-stream'))
        L.append('')
        L.append(value)
    L.append('--' + BOUNDARY + '--')
    L.append('')
    body = CRLF.join(L)
    content_type = 'multipart/form-data; boundary=%s' % BOUNDARY
    return content_type, body


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


def __mod_network_settings_command__(**kwargs):
    # TODO: This has not yet been exported to any django management command.
    # As a result only defaults are used, but are good enough for now.

    for i in kwargs.keys():
        if kwargs[i] is None:
            kwargs.pop(i)
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


def __mod_global_settings_command__(**kwargs):
    for i in kwargs.keys():
        if kwargs[i] is None:
            kwargs.pop(i)

    serial_speeds = {
        '9600': '1',
        '19200': '2',
        '38400': '3',
        '57600': '4',
        '115200': '5',
    }
    if 'serial_cli_speed' in kwargs:
        try:
            kwargs['serial_cli_speed'] = serial_speeds[kwargs['serial_cli_speed']]
        except KeyError:
            raise RuntimeError('Serial speed given makes no sense for iLO3 backend')

    kwargs.setdefault('session_timeout', '30')
    kwargs.setdefault('ilo_enabled', 'Y')
    kwargs.setdefault('f8_prompt_enabled', 'Y')
    kwargs.setdefault('f8_login_required', 'N')
    kwargs.setdefault('https_port', '443')
    kwargs.setdefault('http_port', '80')
    kwargs.setdefault('remote_console_port', '17990')
    kwargs.setdefault('virtual_media_port', '17988')
    kwargs.setdefault('ssh_port', '22')
    kwargs.setdefault('ssh_status', 'Y')
    kwargs.setdefault('serial_cli_status', '3')
    kwargs.setdefault('serial_cli_speed', '5')
    kwargs.setdefault('min_password', '8')
    kwargs.setdefault('auth_fail_logging', '3')
    kwargs.setdefault('rbsu_post_ip', 'Y')
    kwargs.setdefault('enforce_aes', 'N')

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
    </MOD_GLOBAL_SETTINGS>
</RIB_INFO>
    ''' % kwargs
    return command


def __boot_order_command__(**kwargs):
    '''
    Valid values: CDROM, FLOPPY, HDD, NETWORK, USB
    '''

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


def __power_on_delay_command__(**kwargs):
    # TODO: This has not yet been exported to any django management command.
    # As a result only defaults are used, but are good enough for now.
    kwargs.setdefault('delay', 'Random')

    command = '''
    <SERVER_INFO MODE="write">
        <SERVER_AUTO_PWR VALUE="%(delay)s" />
    </SERVER_INFO>
    ''' % kwargs
    return command


def __license_set_command__(**kwargs):
    command = '''
    <RIB_INFO MODE="write">
        <LICENSE>
        <ACTIVATE KEY="%(license)s"/>
        </LICENSE>
    </RIB_INFO>
    ''' % kwargs
    return command


def __mod_directory_command__(**kwargs):
    for i in kwargs.keys():
        if kwargs[i] is None:
            kwargs.pop(i)
    kwargs.setdefault('ldap_enable', 'No')
    kwargs.setdefault('local_users_enable', 'Yes')
    kwargs.setdefault('ldap_server', '')
    kwargs.setdefault('lom_dn', '')
    kwargs.setdefault('lom_password', '')
    kwargs.setdefault('ldap_group_enable', 'yes')
    kwargs.setdefault('kerberos_enable', 'N')
    kwargs.setdefault('kerberos_realm', '')
    kwargs.setdefault('kdc_ip', '')
    kwargs.setdefault('kdc_port', '88')

    # TODO: Fix this.
    # Now this is gonna be ugly. Normally we should read the current config
    # and edit it. Unfortunately iLO3 returns unparsable output. So we fall
    # back to always setting the entire configuration for now

    # Contexts handling
    kwargs.setdefault('contexts', ())
    i = 0
    contexts_command = ''
    for _ in kwargs['contexts']:
        contexts_command += '<DIR_USER_CONTEXT_%s VALUE="%s"/>' % (i + 1, kwargs['contexts'][i])
        i = i + 1

    # Group names handling
    kwargs.setdefault('groupnames', ())
    i = 0
    groupnames_command = ''
    for _ in kwargs['groupnames']:
        groupnames_command += '<DIR_GRPACCT%s_NAME VALUE="%s"/>' % (i + 1, kwargs['groupnames'][i])
        i = i + 1

    # Group PRIVs handling
    kwargs.setdefault('groupprivs', ())
    i = 0
    groupprivs_command = ''
    for _ in kwargs['groupprivs']:
        groupprivs_command += '<DIR_GRPACCT%s_PRIV VALUE="%s"/>' % (i + 1, kwargs['groupprivs'][i])
        i = i + 1

    # Group SIDs handling
    kwargs.setdefault('groupsids', ())
    i = 0
    groupsids_command = ''
    for _ in kwargs['groupsids']:
        groupsids_command += '<DIR_GRPACCT%s_SID VALUE="%s"/>' % (i + 1, kwargs['groupsids'][i])
        i = i + 1

    othersettings = '''
            <DIR_AUTHENTICATION_ENABLED VALUE="%(ldap_enable)s"/>
            <DIR_LOCAL_USER_ACCT VALUE="%(local_users_enable)s"/>
            <DIR_SERVER_ADDRESS VALUE="%(ldap_server)s"/>
            <DIR_SERVER_PORT VALUE="636"/>
            <DIR_OBJECT_DN VALUE="%(lom_dn)s"/>
            <DIR_OBJECT_PASSWORD VALUE="%(lom_password)s"/>
            <DIR_ENABLE_GRP_ACCT VALUE="%(ldap_group_enable)s"/>
            <DIR_KERBEROS_ENABLED VALUE="%(kerberos_enable)s"/>
            <DIR_KERBEROS_REALM VALUE="%(kerberos_realm)s"/>
            <DIR_KERBEROS_KDC_ADDRESS VALUE="%(kdc_ip)s"/>
            <DIR_KERBEROS_KDC_PORT VALUE="%(kdc_port)s"/>
    ''' % kwargs

    command = '''
    <DIR_INFO mode="write">
        <MOD_DIR_CONFIG>
        %s
        %s
        %s
        %s
        %s
        </MOD_DIR_CONFIG>
    </DIR_INFO>
    ''' % (othersettings, contexts_command, groupnames_command, groupprivs_command, groupsids_command)
    return command


def __reset_rib_command__():
    command = '''
    <RIB_INFO MODE="write">
        <RESET_RIB/>
    </RIB_INFO>
    '''
    return command.strip()


def __factory_defaults_command__():
    command = '''
    <RIB_INFO MODE="write">
        <FACTORY_DEFAULTS/>
    </RIB_INFO>
    '''
    return command.strip()


def __add_user_command__(**kwargs):
    kwargs.setdefault('admin', 'N')
    kwargs.setdefault('remote_console', 'Y')
    kwargs.setdefault('reset_server', 'Y')
    kwargs.setdefault('virtual_media', 'Y')
    kwargs.setdefault('config_ilo', 'N')

    command = '''
    <USER_INFO MODE="write">
     <ADD_USER
      USER_NAME="%(newuser_fullname)s"
      USER_LOGIN="%(newuser_username)s"
      PASSWORD="%(newuser_password)s">
       <ADMIN_PRIV value ="%(admin)s"/>
       <REMOTE_CONS_PRIV value ="%(remote_console)s"/>
       <RESET_SERVER_PRIV value ="%(reset_server)s"/>
       <VIRTUAL_MEDIA_PRIV value ="%(virtual_media)s"/>
       <CONFIG_ILO_PRIV value="%(config_ilo)s"/>
     </ADD_USER>
    </USER_INFO>
    ''' % kwargs
    return command.strip()


def __get_all_users_command__(**kwargs):
    command = '''
    <USER_INFO MODE="read">
    <GET_ALL_USERS />
    </USER_INFO>
    '''
    return command.strip()


def __remove_user_command__(**kwargs):
    command = '''
    <USER_INFO MODE="write">
     <DELETE_USER USER_LOGIN="%(deluser_username)s"/>
    </USER_INFO>
    ''' % kwargs
    return command.strip()


def __firmware_update_command__(**kwargs):
    command = '''
    <RIB_INFO MODE="write">
     <TPM_ENABLED VALUE="Yes"/>
     <UPDATE_RIB_FIRMWARE IMAGE_LOCATION="%(firmware_location)s"/>
    </RIB_INFO>
    ''' % kwargs
    return command.strip()
