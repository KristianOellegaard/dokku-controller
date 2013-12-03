import json
from django.db import models
from django_extensions.db.fields import UUIDField
from dokku_controller.models import App, EnvironmentVariable
import requests


class ServiceRegion(models.Model):
    name = models.CharField(max_length=64, blank=True)
    code = models.CharField(max_length=64, primary_key=True)

    def __unicode__(self):
        return self.name if self.name else self.code


class Service(models.Model):
    uuid = UUIDField(version=4, primary_key=True, auto=True)
    name = models.CharField(max_length=128)
    manifest = models.FileField(upload_to="manifests/")

    # Extracted from the manifest!
    base_url = models.CharField(max_length=256, editable=False)
    service_id = models.CharField(max_length=256, editable=False)
    password = models.CharField(max_length=256, editable=False)
    sso_salt = models.CharField(max_length=256, editable=False)
    sso_url = models.CharField(max_length=256, editable=False)
    regions = models.ManyToManyField(ServiceRegion, editable=False)

    def __unicode__(self):
        return str(self.uuid)

    def save(self, *args, **kwargs):
        s = super(Service, self).save(*args, **kwargs)
        regions = []
        if not self.base_url or not self.service_id or not self.password or not self.password or not self.sso_salt\
                or not self.sso_url:
            with open(self.manifest.path) as f_obj:
                data = json.load(f_obj)
                self.service_id = data['id']
                self.base_url = data['api']['production']['base_url']
                self.sso_url = data['api']['production']['sso_url']
                self.password = data['api']['password']
                self.sso_salt = data['api']['sso_salt']
                regions = data['api']['regions']
                self.save()
        for region in regions:
            if not self.regions.filter(code=region).exists():
                obj = ServiceRegion.objects.create(code=region)
                self.regions.add(obj)

        return s


class ServicePlan(models.Model):
    service = models.ForeignKey(Service)

    uuid = UUIDField(version=4, primary_key=True, auto=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return str(self.name)


class ServiceAssociation(models.Model):
    app = models.ForeignKey(App)
    service_plan = models.ForeignKey(ServicePlan)
    region = models.ForeignKey(ServiceRegion)

    uuid = UUIDField(version=4, primary_key=True, auto=True)
    service_reference = models.CharField(max_length=128, editable=False, blank=True, null=True)

    def __unicode__(self):
        return str(self.uuid)

    def save(self, *args, **kwargs):
        s = super(ServiceAssociation, self).save(*args, **kwargs)
        if not self.service_reference:
            r = requests.post(self.service_plan.service.base_url, json.dumps({
                "heroku_id": "app123@heroku.com",
                "plan": self.service_plan.name,
                "region": self.region.code,
                #"callback_url": "https://api.heroku.com/vendor/apps/app123%40heroku.com",
                #"logplex_token": "t.abc123",
                #"options": {}
            }), headers={'content-type': 'application/json'})
            if r.status_code == 422:
                raise Exception("Message from server: %s" % r.json()['message'])
            print r.text
            data = r.json()
            self.service_reference = data['id']
            for key, value in data['config'].items():
                ServiceAssociationEnvironmentVariable.objects.create(
                    service_association=self,
                    key=key,
                    value=value,
                    app=self.app,
                )
        return s


class ServiceAssociationEnvironmentVariable(EnvironmentVariable):
    service_association = models.ForeignKey(ServiceAssociation)