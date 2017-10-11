# -*- coding: utf-8 -*- vim:fileencoding=utf-8:
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab

# Copyright © 2014 Alexandros Kosiaris
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
Django management command to import from racktables software
'''

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext_lazy as _l
from hwdoc.models import RackRow, Rack, Datacenter, RackModel, RackPosition, \
    Vendor, EquipmentModel, Equipment
from keyvalue.models import Key, KeyValue

import MySQLdb
from MySQLdb.cursors import DictCursor

from optparse import make_option
import re
import datetime
import string
import random


class Command(BaseCommand):
    '''
    Django management command to import from racktables database
    '''
    help = _l('Populates hwdoc from a racktables mysql database')
    args = ''

    option_list = BaseCommand.option_list + (
        make_option('-H', '--host',
                    action='store',
                    type='string',
                    dest='host',
                    default='localhost',
                    help=_l('Racktables MySQL database host. Defaults to localhost')),
        make_option('-u', '--user',
                    action='store',
                    type='string',
                    dest='user',
                    help=_l('Racktables MySQL database user [required]')),
        make_option('-p', '--password',
                    action='store',
                    type='string',
                    dest='password',
                    help=_l('Racktables MySQL database password [required]')),
        make_option('-P', '--port',
                    action='store',
                    type='int',
                    dest='port',
                    default=3306,
                    help=_l('Racktables MySQL database port. Defaults to 3306')),
        make_option('-d', '--database',
                    action='store',
                    type='string',
                    dest='database',
                    default='racktables',
                    help=_l('Racktables MySQL database name. Defaults to racktables')),
    )

    def handle(self, *args, **options):
        '''
        Handle command
        '''
        if not options['user'] or not options['password']:
            print('Required option user or password not specified')
            return

        db = MySQLdb.connect(
            host=options['host'],
            port=options['port'],
            db=options['database'],
            user=options['user'],
            passwd=options['password'],
            cursorclass=DictCursor)
        c = db.cursor()
        # Let's get all Rows and locations first
        c.execute('SELECT name, location_name from Row')
        rows = c.fetchall()
        dc_count = 0
        row_count = 0
        rack_count = 0
        eq_count = 0
        for row in rows:
            dc_name = row['location_name']
            row_name = row['name']
            if row['location_name'] is None:
                print('Row: %s does not have a location, skipping' % row_name)
                continue
            dc, created = Datacenter.objects.get_or_create(name=dc_name)
            if created:
                dc_count = dc_count + 1
            row, created = RackRow.objects.get_or_create(dc=dc, name=row_name)
            if created:
                row_count = row_count + 1
        # Then Racks
        c.execute(
            '''
            SELECT Rack.name,
                   Rack.height,
                   Rack.sort_order,
                   Row.name AS row_name,
                   Row.location_name
            FROM Rack
            JOIN Row ON
                Rack.row_id = Row.id
            ''')
        racks = c.fetchall()
        for rack in racks:
            try:
                row = RackRow.objects.get(dc__name=rack['location_name'], name=rack['row_name'])
            except RackRow.DoesNotExist:
                print('RackRow does not exist: %s. Skipping rack %s, probably it did not have a location' % (rack['row_name'], rack['name']))
                continue
            # TODO: Actually find the rack models
            try:
                rm = RackModel.objects.get(id=1)
            except RackModel.DoesNotExist:
                print('No RackModels found, have you loaded vendor-model data?  Exiting')
                return
            r, created = Rack.objects.get_or_create(
                name=rack['name'],
                rackposition__rr=row,
                mounted_depth=rack['height'],
                model=rm)
            if created:
                rack_count = rack_count + 1
            RackPosition.objects.get_or_create(rack=r, rr=row, position=rack['sort_order'])
        # Get the actual object. The union seemingly same select is for getting zero_u objects
        c.execute(
            '''
            SELECT  Object.name AS object_name,
                    Object.label AS object_label,
                    Object.asset_no AS asset_tag,
                    Attribute.name AS attribute_name,
                    AttributeValue.string_value AS attribute_string,
                    AttributeValue.float_value AS attribute_float,
                    AttributeValue.uint_value AS attribute_uint,
                    Dictionary.dict_value AS dict_value,
                    Attribute.type AS attribute_type,
                    Rack.name AS rack_name,
                    Rack.row_name,
                    RackSpace.unit_no,
                    RackSpace.atom,
                    Row.location_name
            FROM Object
            JOIN AttributeValue
                ON Object.id = AttributeValue.object_id
            JOIN AttributeMap
                ON AttributeMap.objtype_id = AttributeValue.object_tid
                AND AttributeMap.attr_id = AttributeValue.attr_id
            JOIN Attribute ON
                Attribute.id = AttributeMap.attr_id
            LEFT JOIN Dictionary ON
                Dictionary.dict_key = AttributeValue.uint_value
            JOIN RackSpace
                ON Object.id = RackSpace.object_id
            JOIN Rack
                ON RackSpace.rack_id = Rack.id
            JOIN Row
                ON Row.id = Rack.row_id
            UNION
            SELECT  Object.name AS object_name,
                    Object.label AS object_label,
                    Object.asset_no AS asset_tag,
                    Attribute.name AS attribute_name,
                    AttributeValue.string_value AS attribute_string,
                    AttributeValue.float_value AS attribute_float,
                    AttributeValue.uint_value AS attribute_uint,
                    Dictionary.dict_value AS dict_value,
                    Attribute.type AS attribute_type,
                    Rack.name AS rack_name,
                    Rack.row_name,
                    0 as unit_no,
                    'zero_u' as atom,
                    Row.location_name
            FROM Object
            JOIN AttributeValue
                ON Object.id = AttributeValue.object_id
            JOIN AttributeMap
                ON AttributeMap.objtype_id = AttributeValue.object_tid
                AND AttributeMap.attr_id = AttributeValue.attr_id
            JOIN Attribute ON
                Attribute.id = AttributeMap.attr_id
            LEFT JOIN Dictionary ON
                Dictionary.dict_key = AttributeValue.uint_value
            JOIN EntityLink
                ON Object.id = EntityLink.child_entity_id
                AND EntityLink.parent_entity_type = 'rack'
            JOIN Rack
                ON Rack.id = EntityLink.parent_entity_id
            JOIN Row
                ON Row.id = Rack.row_id
            ''')
        objects = c.fetchall()
        equipments = dict()
        for obj in objects:
            decommissioned = False
            object_name = obj['object_name'].lower()
            try:
                dc_name = obj['location_name']
                row_name = obj['row_name']
                rack_name = obj['rack_name']
                dc = Datacenter.objects.get(name=dc_name)
                row = RackRow.objects.get(dc=dc, name=row_name)
                r = Rack.objects.get(name=rack_name, rackposition__rr=row)
            except Datacenter.DoesNotExist:
                if obj['row_name'] == 'decommissioned':
                    decommissioned = True
                else:
                    print('Object: %s has a dc that does not exist: %s' % (object_name, dc_name))
                    continue
            except RackRow.DoesNotExist:
                print('Object: %s has a row that does not exist: %s' % (object_name, row_name))
                continue
            except Rack.DoesNotExist:
                print('Object: %s has a rack that does not exist: %s' % (object_name, rack_name))
                continue
            try:
                equipments[object_name]
            except KeyError:
                equipments[object_name] = dict()
                equipments[object_name]['attrs'] = dict()
                equipments[object_name]['attrs']['Asset Name'] = object_name
                equipments[object_name]['rack_front'] = False
                equipments[object_name]['rack_interior'] = False
                equipments[object_name]['rack_back'] = False
            equipments[object_name]['rack'] = r
            equipments[object_name]['attrs']['Asset Tag'] = obj['asset_tag']
            if obj['atom'] == 'front':
                equipments[object_name]['rack_front'] = True
            elif obj['atom'] == 'interior':
                equipments[object_name]['rack_interior'] = True
            elif obj['atom'] == 'rear':
                equipments[object_name]['rack_back'] = True
            if 'min_unit' in equipments[object_name]:
                if equipments[object_name]['min_unit'] > obj['unit_no']:
                    equipments[object_name]['min_unit'] = obj['unit_no']
            else:
                equipments[object_name]['min_unit'] = obj['unit_no']
            if 'max_unit' in equipments[object_name]:
                if equipments[object_name]['max_unit'] < obj['unit_no']:
                    equipments[object_name]['max_unit'] = obj['unit_no']
            else:
                equipments[object_name]['max_unit'] = obj['unit_no']
            equipments[object_name]['unit'] = equipments[object_name]['min_unit']
            equipments[object_name]['u'] = equipments[object_name]['max_unit'] - equipments[object_name]['min_unit'] + 1
            if obj['attribute_name'] == 'OEM S/N 1':
                equipments[object_name]['serial'] = obj['attribute_string']
            elif obj['attribute_name'] == 'HW warranty expiration':
                if obj['attribute_uint']:
                    equipments[object_name]['attrs']['warranty'] = datetime.datetime.utcfromtimestamp(obj['attribute_uint']).strftime('%Y-%m-%d')
                else:
                    equipments[object_name]['attrs']['warranty'] = obj['attribute_string']
            elif obj['attribute_name'] == 'WMF Owned':
                equipments[object_name]['attrs']['wmf_owned'] = obj['dict_value']
            elif obj['attribute_name'] == 'Purchase Date':
                equipments[object_name]['attrs']['Purchase Date'] = obj['attribute_string']
            elif obj['attribute_name'] == 'Purchase Price':
                equipments[object_name]['Purchase Price'] = str(obj['attribute_float'])
            elif obj['attribute_name'] == 'Invoice #':
                equipments[object_name]['attrs']['Invoice'] = obj['attribute_string']
            elif obj['attribute_name'] == 'Procurement RT #':
                equipments[object_name]['attrs']['Procurement RT #'] = obj['attribute_uint']
            elif obj['attribute_name'] == 'HW type':
                m = re.search('([\w\d]+)(?:\s|%GSKIP%|%GPASS%)?([\w\d\.-]+(?:\s|%GPASS%)?[\w\d\s\.-]+)', obj['dict_value'])
                if m:
                    vendor, eq_model = m.groups()
                    eq_model = eq_model.replace('%GPASS%', ' ')
                    equipments[object_name]['vendor'] = vendor
                    equipments[object_name]['eq_model'] = eq_model
                else:
                    print('No HW Type!!!' + obj['dict_value'])
            if decommissioned:
                equipments[object_name]['attrs']['Tag'] = 'decommissioned'
                equipments[object_name]['rack'] = None
                equipments[object_name]['unit'] = None
                equipments[object_name]['rack_front'] = False
                equipments[object_name]['rack_interior'] = False
                equipments[object_name]['rack_back'] = False
                # We know none of the below for these equipments, but don't want
                # to ditch them so assign them something hardcoded and/or
                # autogenerated
                equipments[object_name]['eq_model'] = 'Unknown Model'
                equipments[object_name]['vendor'] = 'Unknown/Unspecified Model'
                chars = string.ascii_lowercase + string.digits
                equipments[object_name]['serial'] = 'DUMMY_SERIAL_%s' % \
                    ''.join(random.choice(chars) for i in range(10))

        serial_missing = []
        model_missing = []
        for k, v in equipments.items():
            flagged = False
            if 'eq_model' not in v:
                model_missing.append(k)
                flagged = True
            if 'serial' not in v:
                serial_missing.append(k)
                flagged = True
            if flagged:
                continue

            vendor, created = Vendor.objects.get_or_create(name=v['vendor'])
            eqm, created = EquipmentModel.objects.get_or_create(
                vendor=vendor,
                name=v['eq_model'],
                u=v['u'])
            e = {
                'model': eqm,
                'serial': v['serial'],
                'rack': v['rack'],
                'unit': v['unit'],
                'rack_front': v['rack_front'],
                'rack_interior': v['rack_interior'],
                'rack_back': v['rack_back'],
            }
            e, created = Equipment.objects.get_or_create(**e)
            if created:
                eq_count = eq_count + 1
            for attr_key, attr_value in v['attrs'].items():
                if attr_value is None:
                    continue
                key, created = Key.objects.get_or_create(name=attr_key)
                # get_or_create will not work with KeyValue due to the
                # GenericForeignKey. Fallback to the standard way
                try:
                    kv = KeyValue.objects.get(
                        key=key, value=attr_value,
                        owner_content_type__name='Equipment',
                        owner_object_id=e.id)
                except KeyValue.DoesNotExist:
                    kv = KeyValue(key=key, value=attr_value, owner_content_object=e)
                    kv.save()

        print('''
        Imported successfully:
        Datacenters: %s
        Rack Rows: %s
        Racks: %s
        Equipments: %s
        ''' % (dc_count, row_count, rack_count, eq_count))
        print('Not migrated because:')
        print('Missing model:')
        print(', '.join(sorted(model_missing)))
        print('Missing serial:')
        print(', '.join(sorted(serial_missing)))
