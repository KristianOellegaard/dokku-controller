from django.db import models
from dokku_controller.models import App


class ServiceAssociation(models.Model):
    app = models.ForeignKey(App)

    service_backend = models.CharField(max_length=128)
    service_reference = models.CharField(max_length=128)
    service_uri = models.CharField(max_length=128)

    def __unicode__(self):
        pass