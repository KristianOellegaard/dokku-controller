# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding field 'Deployment.status'
        db.add_column(u'dokku_controller_deployment', 'status',
                      self.gf('django.db.models.fields.CharField')(default='deployed_success', max_length=32),
                      keep_default=False)

        # Adding field 'Deployment.revision'
        db.add_column(u'dokku_controller_deployment', 'revision',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.Revision'], null=True),
                      keep_default=False)


    def backwards(self, orm):
        # Deleting field 'Deployment.status'
        db.delete_column(u'dokku_controller_deployment', 'status')

        # Deleting field 'Deployment.revision'
        db.delete_column(u'dokku_controller_deployment', 'revision_id')


    models = {
        u'dokku_controller.app': {
            'Meta': {'object_name': 'App'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'primary_key': 'True'}),
            'paused': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'dokku_controller.deployment': {
            'Meta': {'object_name': 'Deployment'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            'endpoint': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'host': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.Host']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_update': ('django.db.models.fields.DateTimeField', [], {}),
            'revision': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.Revision']", 'null': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'max_length': '32'})
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
            'date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'revision_number': ('django.db.models.fields.IntegerField', [], {})
        }
    }

    complete_apps = ['dokku_controller']