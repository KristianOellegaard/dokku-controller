# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'ServiceRegion'
        db.create_table(u'service_gw_serviceregion', (
            ('name', self.gf('django.db.models.fields.CharField')(max_length=64, blank=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=64, primary_key=True)),
        ))
        db.send_create_signal(u'service_gw', ['ServiceRegion'])

        # Adding model 'Service'
        db.create_table(u'service_gw_service', (
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('manifest', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('base_url', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('service_id', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('sso_salt', self.gf('django.db.models.fields.CharField')(max_length=256)),
            ('sso_url', self.gf('django.db.models.fields.CharField')(max_length=256)),
        ))
        db.send_create_signal(u'service_gw', ['Service'])

        # Adding M2M table for field regions on 'Service'
        m2m_table_name = db.shorten_name(u'service_gw_service_regions')
        db.create_table(m2m_table_name, (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('service', models.ForeignKey(orm[u'service_gw.service'], null=False)),
            ('serviceregion', models.ForeignKey(orm[u'service_gw.serviceregion'], null=False))
        ))
        db.create_unique(m2m_table_name, ['service_id', 'serviceregion_id'])

        # Adding model 'ServicePlan'
        db.create_table(u'service_gw_serviceplan', (
            ('service', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_gw.Service'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=128)),
        ))
        db.send_create_signal(u'service_gw', ['ServicePlan'])

        # Adding model 'ServiceAssociation'
        db.create_table(u'service_gw_serviceassociation', (
            ('app', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['dokku_controller.App'])),
            ('service_plan', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_gw.ServicePlan'])),
            ('region', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_gw.ServiceRegion'])),
            ('uuid', self.gf('django.db.models.fields.CharField')(max_length=36, primary_key=True)),
            ('service_reference', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
        ))
        db.send_create_signal(u'service_gw', ['ServiceAssociation'])

        # Adding model 'ServiceAssociationEnvironmentVariable'
        db.create_table(u'service_gw_serviceassociationenvironmentvariable', (
            (u'environmentvariable_ptr', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['dokku_controller.EnvironmentVariable'], unique=True, primary_key=True)),
            ('service_association', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['service_gw.ServiceAssociation'])),
        ))
        db.send_create_signal(u'service_gw', ['ServiceAssociationEnvironmentVariable'])


    def backwards(self, orm):
        # Deleting model 'ServiceRegion'
        db.delete_table(u'service_gw_serviceregion')

        # Deleting model 'Service'
        db.delete_table(u'service_gw_service')

        # Removing M2M table for field regions on 'Service'
        db.delete_table(db.shorten_name(u'service_gw_service_regions'))

        # Deleting model 'ServicePlan'
        db.delete_table(u'service_gw_serviceplan')

        # Deleting model 'ServiceAssociation'
        db.delete_table(u'service_gw_serviceassociation')

        # Deleting model 'ServiceAssociationEnvironmentVariable'
        db.delete_table(u'service_gw_serviceassociationenvironmentvariable')


    models = {
        u'dokku_controller.app': {
            'Meta': {'object_name': 'App'},
            'can_pause': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '128', 'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'new'", 'max_length': '64'}),
            'web_concurrency': ('django.db.models.fields.IntegerField', [], {'default': '1'})
        },
        u'dokku_controller.environmentvariable': {
            'Meta': {'object_name': 'EnvironmentVariable'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            'id': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'}),
            'key': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'value': ('django.db.models.fields.CharField', [], {'max_length': '256'})
        },
        u'service_gw.service': {
            'Meta': {'object_name': 'Service'},
            'base_url': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'manifest': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'regions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['service_gw.ServiceRegion']", 'symmetrical': 'False'}),
            'service_id': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'sso_salt': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'sso_url': ('django.db.models.fields.CharField', [], {'max_length': '256'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        },
        u'service_gw.serviceassociation': {
            'Meta': {'object_name': 'ServiceAssociation'},
            'app': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['dokku_controller.App']"}),
            'region': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service_gw.ServiceRegion']"}),
            'service_plan': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service_gw.ServicePlan']"}),
            'service_reference': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        },
        u'service_gw.serviceassociationenvironmentvariable': {
            'Meta': {'object_name': 'ServiceAssociationEnvironmentVariable', '_ormbases': [u'dokku_controller.EnvironmentVariable']},
            u'environmentvariable_ptr': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['dokku_controller.EnvironmentVariable']", 'unique': 'True', 'primary_key': 'True'}),
            'service_association': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service_gw.ServiceAssociation']"})
        },
        u'service_gw.serviceplan': {
            'Meta': {'object_name': 'ServicePlan'},
            'name': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'service': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['service_gw.Service']"}),
            'uuid': ('django.db.models.fields.CharField', [], {'max_length': '36', 'primary_key': 'True'})
        },
        u'service_gw.serviceregion': {
            'Meta': {'object_name': 'ServiceRegion'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '64', 'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '64', 'blank': 'True'})
        }
    }

    complete_apps = ['service_gw']