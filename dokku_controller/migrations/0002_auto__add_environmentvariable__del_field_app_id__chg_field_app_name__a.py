# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'EnvironmentVariable'
        db.create_table(u'dokku_controller_environmentvariable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'dokku_controller', ['EnvironmentVariable'])

        # Deleting field 'App.id'
        db.delete_column(u'dokku_controller_app', u'id')


        # Changing field 'App.name'
        db.alter_column(u'dokku_controller_app', 'name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, primary_key=True))
        # Adding unique constraint on 'App', fields ['name']
        db.create_unique(u'dokku_controller_app', ['name'])


    def backwards(self, orm):
        # Removing unique constraint on 'App', fields ['name']
        db.delete_unique(u'dokku_controller_app', ['name'])

        # Deleting model 'EnvironmentVariable'
        db.delete_table(u'dokku_controller_environmentvariable')


        # User chose to not deal with backwards NULL issues for 'App.id'
        raise RuntimeError("Cannot reverse this migration. 'App.id' and its values cannot be restored.")
        
        # The following code is provided here to aid in writing a correct migration        # Adding field 'App.id'
        db.add_column(u'dokku_controller_app', u'id',
                      self.gf('django.db.models.fields.AutoField')(primary_key=True),
                      keep_default=False)


        # Changing field 'App.name'
        db.alter_column(u'dokku_controller_app', 'name', self.gf('django.db.models.fields.CharField')(max_length=128))

    models = {
        u'dokku_controller.app': {
            'Meta': {'object_name': 'App'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'primary_key': 'True'})
        },
        u'dokku_controller.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'dokku_controller.domain': {
            'Meta': {'object_name': 'Domain'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            'domain_name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'primary_key': 'True'})
        },
        u'dokku_controller.environmentvariable': {
            'Meta': {'object_name': 'EnvironmentVariable'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'dokku_controller.host': {
            'Meta': {'object_name': 'Host'},
            'hostname': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['dokku_controller']