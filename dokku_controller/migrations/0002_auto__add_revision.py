# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Revision'
        db.create_table(u'dokku_controller_revision', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('date', self.gf('django.db.models.fields.DateTimeField')()),
            ('revision_number', self.gf('django.db.models.fields.IntegerField')()),
            ('compressed_archive', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
        ))
        db.send_create_signal(u'dokku_controller', ['Revision'])


    def backwards(self, orm):
        # Deleting model 'Revision'
        db.delete_table(u'dokku_controller_revision')


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
        },
        u'dokku_controller.revision': {
            'Meta': {'object_name': 'Revision'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            'compressed_archive': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['dokku_controller']