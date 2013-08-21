from django.db import models
from dokku_controller.tasks import restart, delete


class Host(models.Model):
    hostname = models.CharField(max_length=128)

    def __unicode__(self):
        return self.hostname


class App(models.Model):
    name = models.CharField(max_length=128)

    def restart(self):
        for deployment in self.deployment_set.all():
            restart(deployment.host.hostname, deployment.app.name)

    def delete(self, *args, **kwargs):
        for deployment in self.deployment_set.all():
            delete(deployment.host.hostname, deployment.app.name)
        return super(App, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Deployment(models.Model):
    host = models.ForeignKey(Host)
    app = models.ForeignKey(App)
    last_update = models.DateTimeField()

    def __unicode__(self):
        return u"%s on %s"  % (self.app.name, self.host.hostname)