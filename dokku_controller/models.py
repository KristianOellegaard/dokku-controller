import datetime
from django.db import models
from django.db.models.signals import post_save
from dokku_controller.tasks import restart, delete, update_environment, deploy_revision, get_new_deployment_server, start, stop, update_load_balancer_config, scan_host_key
from project.redis_connection import connection as redis_connection
from django.conf import settings

class Host(models.Model):
    hostname = models.CharField(max_length=128)

    def __unicode__(self):
        return self.hostname


class App(models.Model):
    name = models.CharField(max_length=128, unique=True, primary_key=True)
    paused = models.BooleanField()

    def start(self):
        for deployment in self.deployment_set.all():
            start(deployment.host.hostname, deployment.app.name)
        self.paused = False
        self.save()

    def stop(self):
        for deployment in self.deployment_set.all():
            stop(deployment.host.hostname, deployment.app.name)

    def restart(self):
        for deployment in self.deployment_set.all():
            restart(deployment.host.hostname, deployment.app.name)
        self.paused = False
        self.save()

    def pause(self):
        self.stop()
        self.paused = True
        self.save()
        update_load_balancer_config([self.pk])

    def update_environment_variables(self):
        for deployment in self.deployment_set.all():
            update_environment(deployment.host.hostname, deployment.app.name, [(var.key, var.value) for var in self.environmentvariable_set.all()])
        self.restart()

    def delete(self, *args, **kwargs):
        for deployment in self.deployment_set.all():
            delete(deployment.host.hostname, deployment.app.name)
        return super(App, self).delete(*args, **kwargs)

    def deploy(self):
        revision = self.revision_set.all().latest('revision_number')
        if self.deployment_set.all():
            for deployment in self.deployment_set.all():
                deploy_revision(
                    deployment.pk,
                    revision.pk,
                )
        else:  # This wasn't deployed to a server before!
            deployment = Deployment.objects.create(
                host=get_new_deployment_server(self),
                app=self,
                revision=revision,
                last_update=datetime.datetime.now() - datetime.timedelta(days=30)  # make it inactive
            )
            deploy_revision(
                deployment.pk,
                revision.pk,
            )

    def __unicode__(self):
        return self.name


class Revision(models.Model):
    app = models.ForeignKey(App)
    date = models.DateTimeField(default=datetime.datetime.now)
    revision_number = models.IntegerField(editable=False)
    compressed_archive = models.FileField(upload_to=lambda instance, filename: "%s/%s-%s" % (
        instance.app.name, instance.revision_number, filename
    ))
    docker_image_name = models.CharField(max_length=128, null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.revision_number:
            revision_count = self.app.revision_set.all().count()
            if revision_count > 0:
                self.revision_number = revision_count + 1
            else:
                self.revision_number = 1
        return super(Revision, self).save(*args, **kwargs)

    def __unicode__(self):
        return u"v%s" % self.revision_number

DEPLOYMENT_STATUS_CHOICES = (
    ('waiting_for_deploy', "Waiting to be deployed"),
    ('deploying', "Deploying"),
    ('deployed_success', "Deployed successfully"),
    ('deployed_error', "Deployment failed"),

)


class Deployment(models.Model):
    host = models.ForeignKey(Host)
    app = models.ForeignKey(App)
    endpoint = models.CharField(max_length=256)
    last_update = models.DateTimeField()
    status = models.CharField(max_length=32, choices=DEPLOYMENT_STATUS_CHOICES, default="waiting_for_deploy")
    error_message = models.TextField()
    revision = models.ForeignKey(Revision, null=True)

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


def save_host(sender, instance, created, *args, **kwargs):
    if created:
        scan_host_key(instance.hostname)

post_save.connect(save_host, sender=Host, dispatch_uid="scan_host_key")