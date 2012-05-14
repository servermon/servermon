# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):
    
    def forwards(self, orm):
        
        # Adding model 'Email'
        db.create_table('hwdoc_email', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('hwdoc', ['Email'])

        # Adding model 'Person'
        db.create_table('hwdoc_person', (
            ('surname', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('hwdoc', ['Person'])

        # Adding M2M table for field phones on 'Person'
        db.create_table('hwdoc_person_phones', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['hwdoc.person'], null=False)),
            ('phone', models.ForeignKey(orm['hwdoc.phone'], null=False))
        ))
        db.create_unique('hwdoc_person_phones', ['person_id', 'phone_id'])

        # Adding M2M table for field emails on 'Person'
        db.create_table('hwdoc_person_emails', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('person', models.ForeignKey(orm['hwdoc.person'], null=False)),
            ('email', models.ForeignKey(orm['hwdoc.email'], null=False))
        ))
        db.create_unique('hwdoc_person_emails', ['person_id', 'email_id'])

        # Adding model 'Phone'
        db.create_table('hwdoc_phone', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('number', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('hwdoc', ['Phone'])

        # Adding model 'Project'
        db.create_table('hwdoc_project', (
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=80)),
        ))
        db.send_create_signal('hwdoc', ['Project'])

        # Adding model 'Role'
        db.create_table('hwdoc_role', (
            ('project', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hwdoc.Project'])),
            ('person', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hwdoc.Person'])),
            ('role', self.gf('django.db.models.fields.CharField')(max_length=80)),
            ('id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
        ))
        db.send_create_signal('hwdoc', ['Role'])

        # Adding field 'Equipment.allocation'
        db.add_column('hwdoc_equipment', 'allocation', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['hwdoc.Project'], null=True, blank=True), keep_default=False)
    
    
    def backwards(self, orm):
        
        # Deleting model 'Email'
        db.delete_table('hwdoc_email')

        # Deleting model 'Person'
        db.delete_table('hwdoc_person')

        # Removing M2M table for field phones on 'Person'
        db.delete_table('hwdoc_person_phones')

        # Removing M2M table for field emails on 'Person'
        db.delete_table('hwdoc_person_emails')

        # Deleting model 'Phone'
        db.delete_table('hwdoc_phone')

        # Deleting model 'Project'
        db.delete_table('hwdoc_project')

        # Deleting model 'Role'
        db.delete_table('hwdoc_role')

        # Deleting field 'Equipment.allocation'
        db.delete_column('hwdoc_equipment', 'allocation_id')
    
    
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
            'emails': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hwdoc.Email']"}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'}),
            'phones': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hwdoc.Phone']"}),
            'surname': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'hwdoc.phone': {
            'Meta': {'object_name': 'Phone'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'number': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        },
        'hwdoc.project': {
            'Meta': {'object_name': 'Project'},
            'contacts': ('django.db.models.fields.related.ManyToManyField', [], {'to': "orm['hwdoc.Person']", 'through': "'Role'"}),
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
        'hwdoc.vendor': {
            'Meta': {'object_name': 'Vendor'},
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80'})
        }
    }
    
    complete_apps = ['hwdoc']
