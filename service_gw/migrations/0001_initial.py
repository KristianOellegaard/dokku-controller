# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ServiceAssociation'
        db.create_table(u'service_gw_serviceassociation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('service_backend', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('service_reference', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('service_uri', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'service_gw', ['ServiceAssociation'])


    def backwards(self, orm):
        # Deleting model 'ServiceAssociation'
        db.delete_table(u'service_gw_serviceassociation')


    models = {
        u'dokku_controller.app': {
            'Meta': {'object_name': 'App'},
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'primary_key': 'True'})
        },
        u'service_gw.serviceassociation': {
            'Meta': {'object_name': 'ServiceAssociation'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'service_backend': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'service_reference': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'service_uri': ('django.db.models.fields.CharField', [], {'max_length': '128'})
        }
    }

    complete_apps = ['service_gw']