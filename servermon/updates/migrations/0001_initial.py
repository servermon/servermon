# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):

        # Adding model 'Package'
        db.create_table('updates_package', (
            ('sourcename', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=200)),
        ))
        db.send_create_signal('updates', ['Package'])

        # Adding model 'Update'
        db.create_table('updates_update', (
            ('candidateVersion', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('package', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['updates.Package'])),
            ('installedVersion', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('source', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['puppet.Host'])),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('updates', ['Update'])


    def backwards(self, orm):

        # Deleting model 'Package'
        db.delete_table('updates_package')

        # Deleting model 'Update'
        db.delete_table('updates_update')


    models = {
        'puppet.fact': {
            'Meta': {'object_name': 'Fact', 'db_table': "u'fact_names'", 'managed': 'False'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'puppet.factvalue': {
            'Meta': {'object_name': 'FactValue', 'db_table': "u'fact_values'", 'managed': 'False'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fact_name': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['puppet.Fact']"}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['puppet.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.TextField', [], {})
        },
        'puppet.host': {
            'Meta': {'object_name': 'Host', 'db_table': "u'hosts'", 'managed': 'False'},
            'created_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'environment': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'facts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['puppet.Fact']", 'through': "orm['puppet.FactValue']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'ip': ('django.db.models.fields.CharField', [], {'max_length': '255', 'blank': 'True'}),
            'last_compile': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_freshcheck': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'last_report': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'source_file_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'updated_at': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        'updates.package': {
            'Meta': {'object_name': 'Package'},
            'hosts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['puppet.Host']", 'through': "orm['updates.Update']", 'symmetrical': 'False'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'sourcename': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        },
        'updates.update': {
            'Meta': {'object_name': 'Update'},
            'candidateVersion': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['puppet.Host']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'installedVersion': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'package': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['updates.Package']"}),
            'source': ('django.db.models.fields.CharField', [], {'max_length': '200'})
        }
    }

    complete_apps = ['updates']
