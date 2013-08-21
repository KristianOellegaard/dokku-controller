from django.db import models
from dokku_controller.tasks import restart, delete, update_environment


class Host(models.Model):
    hostname = models.CharField(max_length=128)

    def __unicode__(self):
        return self.hostname


class App(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key=True)

    def restart(self):
        for deployment in self.deployment_set.all():
            restart(deployment.host.hostname, deployment.app.name)

    def update_environment_variables(self):
        for deployment in self.deployment_set.all():
            update_environment(deployment.host.hostname, deployment.app.name, [(var.key, var.value) for var in self.environmentvariable_set.all()])
        self.restart()

    def delete(self, *args, **kwargs):
        for deployment in self.deployment_set.all():
            delete(deployment.host.hostname, deployment.app.name)
        return super(App, self).delete(*args, **kwargs)

    def __unicode__(self):
        return self.name


class Deployment(models.Model):
    host = models.ForeignKey(Host)
    app = models.ForeignKey(App)
    endpoint = models.CharField(max_length=256)
    last_update = models.DateTimeField()

    def __unicode__(self):
        return u"%s on %s" % (self.app.name, self.host.hostname)


class Domain(models.Model):
    app = models.ForeignKey(App)
    domain_name = models.CharField(max_length=128, unique=True, primary_key=True)

    def __unicode__(self):
        return self.domain_name


class EnvironmentVariable(models.Model):
    app = models.ForeignKey(App)
    key = models.CharField(max_length=256)
    value = models.CharField(max_length=256)

    def __unicode__(self):
        return u"%s=%s" % (self.key, self.value)