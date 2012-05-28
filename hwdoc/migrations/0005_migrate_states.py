# -*- coding: utf-8 -*-
# vim: tabstop=4:shiftwidth=4:softtabstop=4:expandtab
import datetime
from south.db import db
from south.v2 import DataMigration
from django.db import models

class Migration(DataMigration):

    def forwards(self, orm):
        equipments = orm['hwdoc.Equipment'].objects.all()
    	try:
            # WORKING - OK => Functional
            equipments.filter(state='0').update(temp=orm['hwdoc.State'].objects.get(name='Functional'))
            # WORKING - RMA => Component RMA
            equipments.filter(state='1').update(temp=orm['hwdoc.State'].objects.get(name='Component RMA'))
            # NOT WORKING - RMA => RMA
            equipments.filter(state='2').update(temp=orm['hwdoc.State'].objects.get(name='RMA'))
            # NOT WORKING - CHECKING => To Be Checked
            equipments.filter(state='3').update(temp=orm['hwdoc.State'].objects.get(name='To Be Checked'))
            # INACTIVE => Functional
            equipments.filter(state='4').update(temp=orm['hwdoc.State'].objects.get(name='Functional'))
            # UNKNOWN => Unknown
            equipments.filter(state='5').update(temp=orm['hwdoc.State'].objects.get(name='Unknown'))
        except orm['hwdoc.State'].DoesNotExist:
            pass

    def backwards(self, orm):
        try:
            equipments = orm['hwdoc.Equipment'].objects.all()
            # WORKING - OK <= Functional
            equipments.filter(temp__name='Functional').update(state=0)
            # WORKING - RMA <= Component RMA
            equipments.filter(temp__name='Component RMA').update(state=1)
            # NOT WORKING - RMA <= RMA
            equipments.filter(temp__name='RMA').update(state=2)
            # NOT WORKING - CHECKING <= To Be Checked
            equipments.filter(temp__name='To Be Checked').update(state=3)
            # NOTE: We have lost state 4 - INACTIVE. It did not make any sense so it was deleted
            # UNKNOWN <= Unknown
            equipments.filter(temp__name='Unknown').update(state=5)
        except orm['hwdoc.State'].DoesNotExist:
            pass

    models = {
        'hwdoc.email': {
            'Meta': {'object_name': 'Email'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        'hwdoc.equipment': {
            'Meta': {'object_name': 'Equipment'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'allocation': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Project']", 'null': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Model']"}),
            'purpose': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'rack': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'temp': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.State']"}),
            'unit': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'hwdoc.model': {
            'Meta': {'object_name': 'Model'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'u': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Vendor']"})
        },
        'hwdoc.person': {
            'Meta': {'object_name': 'Person'},
            'emails': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hwdoc.Email']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'phones': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hwdoc.Phone']", 'symmetrical': 'False'}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'hwdoc.phone': {
            'Meta': {'object_name': 'Phone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'hwdoc.project': {
            'Meta': {'object_name': 'Project'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hwdoc.Person']", 'through': "orm['hwdoc.Role']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'hwdoc.role': {
            'Meta': {'object_name': 'Role'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'person': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Person']"}),
            'project': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Project']"}),
            'role': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'hwdoc.servermanagement': {
            'Meta': {'object_name': 'ServerManagement'},
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'equipment': ('django.db.models.fields.related.OneToOneField', [], {'to': "orm['hwdoc.Equipment']", 'unique': 'True'}),
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'license': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'mac': ('django.db.models.fields.CharField', [], {'max_length': '17', 'null': 'True', 'blank': 'True'}),
            'method': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'raid_license': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'})
        },
        'hwdoc.state': {
            'Meta': {'object_name': 'State'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        'hwdoc.vendor': {
            'Meta': {'object_name': 'Vendor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }

    complete_apps = ['hwdoc']
    symmetrical = True
