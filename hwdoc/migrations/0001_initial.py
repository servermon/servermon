# -*- coding: utf-8 -*- vim:fileencoding=utf-8:

from south.db import db
from django.db import models
from servermon.hwdoc.models import *

class Migration:
    
    def forwards(self, orm):
        
        # Adding model 'Vendor'
        db.create_table('hwdoc_vendor', (
            ('id', orm['hwdoc.Vendor:id']),
            ('name', orm['hwdoc.Vendor:name']),
        ))
        db.send_create_signal('hwdoc', ['Vendor'])
        
        # Adding model 'ServerManagement'
        db.create_table('hwdoc_servermanagement', (
            ('id', orm['hwdoc.ServerManagement:id']),
            ('equipment', orm['hwdoc.ServerManagement:equipment']),
            ('method', orm['hwdoc.ServerManagement:method']),
            ('added', orm['hwdoc.ServerManagement:added']),
            ('updated', orm['hwdoc.ServerManagement:updated']),
            ('hostname', orm['hwdoc.ServerManagement:hostname']),
            ('username', orm['hwdoc.ServerManagement:username']),
            ('password', orm['hwdoc.ServerManagement:password']),
            ('license', orm['hwdoc.ServerManagement:license']),
            ('raid_license', orm['hwdoc.ServerManagement:raid_license']),
            ('mac', orm['hwdoc.ServerManagement:mac']),
        ))
        db.send_create_signal('hwdoc', ['ServerManagement'])
        
        # Adding model 'Equipment'
        db.create_table('hwdoc_equipment', (
            ('id', orm['hwdoc.Equipment:id']),
            ('model', orm['hwdoc.Equipment:model']),
            ('serial', orm['hwdoc.Equipment:serial']),
            ('rack', orm['hwdoc.Equipment:rack']),
            ('unit', orm['hwdoc.Equipment:unit']),
            ('purpose', orm['hwdoc.Equipment:purpose']),
            ('comments', orm['hwdoc.Equipment:comments']),
            ('added', orm['hwdoc.Equipment:added']),
            ('updated', orm['hwdoc.Equipment:updated']),
            ('state', orm['hwdoc.Equipment:state']),
        ))
        db.send_create_signal('hwdoc', ['Equipment'])
        
        # Adding model 'Model'
        db.create_table('hwdoc_model', (
            ('id', orm['hwdoc.Model:id']),
            ('vendor', orm['hwdoc.Model:vendor']),
            ('name', orm['hwdoc.Model:name']),
            ('u', orm['hwdoc.Model:u']),
        ))
        db.send_create_signal('hwdoc', ['Model'])
        
    
    
    def backwards(self, orm):
        
        # Deleting model 'Vendor'
        db.delete_table('hwdoc_vendor')
        
        # Deleting model 'ServerManagement'
        db.delete_table('hwdoc_servermanagement')
        
        # Deleting model 'Equipment'
        db.delete_table('hwdoc_equipment')
        
        # Deleting model 'Model'
        db.delete_table('hwdoc_model')
        
    
    
    models = {
        'hwdoc.equipment': {
            'added': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'comments': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Model']"}),
            'purpose': ('django.db.models.fields.CharField', [], {'max_length': '80', 'null': 'True', 'blank': 'True'}),
            'rack': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'serial': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'state': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'unit': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'updated': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'})
        },
        'hwdoc.model': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'u': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'vendor': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['hwdoc.Vendor']"})
        },
        'hwdoc.servermanagement': {
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
        'hwdoc.vendor': {
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }
    
    complete_apps = ['hwdoc']
