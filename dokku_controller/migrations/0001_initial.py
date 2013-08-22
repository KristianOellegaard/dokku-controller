# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Host'
        db.create_table(u'dokku_controller_host', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('hostname', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'dokku_controller', ['Host'])

        # Adding model 'App'
        db.create_table(u'dokku_controller_app', (
            ('name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, primary_key=True)),
        ))
        db.send_create_signal(u'dokku_controller', ['App'])

        # Adding model 'Deployment'
        db.create_table(u'dokku_controller_deployment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('host', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.Host'])),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('endpoint', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('last_update', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'dokku_controller', ['Deployment'])

        # Adding model 'Domain'
        db.create_table(u'dokku_controller_domain', (
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('domain_name', self.gf('django.db.models.fields.CharField')(unique=True, max_length=128, primary_key=True)),
        ))
        db.send_create_signal(u'dokku_controller', ['Domain'])

        # Adding model 'EnvironmentVariable'
        db.create_table(u'dokku_controller_environmentvariable', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('key', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('value', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'dokku_controller', ['EnvironmentVariable'])


    def backwards(self, orm):
        # Deleting model 'Host'
        db.delete_table(u'dokku_controller_host')

        # Deleting model 'App'
        db.delete_table(u'dokku_controller_app')

        # Deleting model 'Deployment'
        db.delete_table(u'dokku_controller_deployment')

        # Deleting model 'Domain'
        db.delete_table(u'dokku_controller_domain')

        # Deleting model 'EnvironmentVariable'
        db.delete_table(u'dokku_controller_environmentvariable')


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