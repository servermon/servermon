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
Module containing dummy implementations of django management commands

Idea is to be able to use it for unit tests and as a reference
'''

def power_on(hostname, username, password):
    '''
    Power on command
    '''
    return True

def power_off(hostname, username, password):
    '''
    Power off command
    '''
    return True

def power_off_acpi(hostname, username, password):
    '''
    Power off using ACPI command
    '''
    return True

def power_cycle(hostname, username, password):
    '''
    Cold boot command
    '''
    return True

def power_reset(hostname, username, password):
    '''
    Warm boot command
    '''
    return True

def pass_change(hostname, username, password, **kwargs):
    '''
    Change BMC password
    '''
    return True

def set_settings(hostname, username, password, **kwargs):
    '''
    Set BMC settings
    '''
    return True

def set_ldap_settings(hostname, username, password, **kwargs):
    '''
    Set BMC LDAP settings
    '''
    return True

def boot_order(hostname, username, password, **kwargs):
    '''
    Set boot order
    '''
    return True

def license_set(hostname, username, password, **kwargs):
    '''
    Set BMC License
    '''
    return True

def bmc_reset(hostname, username, password, **kwargs):
    '''
    Reset BMC
    '''
    return True

def bmc_factory_defaults(hostname, username, password, **kwargs):
    '''
    Reset BMC to factory defaults
    '''
    return True

def add_user(hostname, username, password, **kwargs):
    '''
    Add a user to the BMC
    '''
    return True

def remove_user(hostname, username, password, **kwargs):
    '''
    Remove a User from the BMC
    '''
    return True

