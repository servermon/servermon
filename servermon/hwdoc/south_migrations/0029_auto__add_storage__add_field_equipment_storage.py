# -*- coding: utf-8 -*-
from south.utils import datetime_utils as datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Storage'
        db.create_table(u'hwdoc_storage', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=80)),
            ('dc', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hwdoc.Datacenter'])),
        ))
        db.send_create_signal(u'hwdoc', ['Storage'])

        # Adding field 'Equipment.storage'
        db.add_column(u'hwdoc_equipment', 'storage',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hwdoc.Storage'], null=True, blank=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting model 'Storage'
        db.delete_table(u'hwdoc_storage')

        # Deleting field 'Equipment.storage'
        db.delete_column(u'hwdoc_equipment', 'storage_id')


    models = {
        u'hwdoc.datacenter': {
            'Meta': {'ordering': "['name']", 'object_name': 'Datacenter'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'hwdoc.email': {
            'Meta': {'object_name': 'Email'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'hwdoc.equipment': {
            'Meta': {'ordering': "['rack', '-unit']", 'object_name': 'Equipment'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Project']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.EquipmentModel']"}),
            'orientation': ('django.db.models.fields.CharField', [], {'default': "'Front'", 'max_length': '10'}),
            'purpose': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'rack': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Rack']", 'null': 'True', 'blank': 'True'}),
            'rack_back': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rack_front': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'rack_interior': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'storage': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Storage']", 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        u'hwdoc.equipmentmodel': {
            'Meta': {'ordering': "['vendor', 'name']", 'object_name': 'EquipmentModel'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'u': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Vendor']"})
        },
        u'hwdoc.person': {
            'Meta': {'object_name': 'Person'},
            'emails': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hwdoc.Email']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'phones': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hwdoc.Phone']", 'symmetrical': 'False'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'hwdoc.phone': {
            'Meta': {'object_name': 'Phone'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'hwdoc.project': {
            'Meta': {'ordering': "['name']", 'object_name': 'Project'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hwdoc.Person']", 'through': u"orm['hwdoc.Role']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'hwdoc.rack': {
            'Meta': {'ordering': "['name']", 'object_name': 'Rack'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.RackModel']"}),
            'mounted_depth': ('django.db.models.fields.PositiveIntegerField', [], {'default': '60', 'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'hwdoc.rackmodel': {
            'Meta': {'object_name': 'RackModel'},
            'height': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'inrow_ac': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'max_mounting_depth': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '10'}),
            'min_mounting_depth': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '10'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Vendor']"}),
            'width': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '10'})
        },
        u'hwdoc.rackposition': {
            'Meta': {'ordering': "['position']", 'object_name': 'RackPosition'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'position': ('django.db.models.fields.PositiveIntegerField', [], {'max_length': '20'}),
            'rack': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['hwdoc.Rack']", 'unique': 'True'}),
            'rr': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.RackRow']"})
        },
        u'hwdoc.rackrow': {
            'Meta': {'ordering': "['name']", 'object_name': 'RackRow'},
            'dc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Datacenter']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'hwdoc.role': {
            'Meta': {'object_name': 'Role'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Person']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Project']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        u'hwdoc.servermanagement': {
            'Meta': {'object_name': 'ServerManagement'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'equipment': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['hwdoc.Equipment']", 'unique': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '17', 'blank': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'raid_license': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '80', 'blank': 'True'})
        },
        u'hwdoc.storage': {
            'Meta': {'ordering': "['name']", 'object_name': 'Storage'},
            'dc': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['hwdoc.Datacenter']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'})
        },
        u'hwdoc.ticket': {
            'Meta': {'object_name': 'Ticket'},
            'equipment': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['hwdoc.Equipment']", 'symmetrical': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '20'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'url': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'})
        },
        u'hwdoc.vendor': {
            'Meta': {'ordering': "['name']", 'object_name': 'Vendor'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['hwdoc']