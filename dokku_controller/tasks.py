import StringIO
from subprocess import Popen, CalledProcessError, PIPE
import datetime
import traceback
from django.db.models import Count
import fabric.api as fabric
from django.conf import settings
from fabric.operations import put, os
import redis
from rq import Queue
import time
from dokku_controller.utils import TemporaryDirectory
from project.redis_connection import connection as redis_connection, pool
import logging
from django.utils.timezone import now

logging.basicConfig(
    format='%(asctime)s,%(msecs)05.1f (%(funcName)s) %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def check_call(cmd, *args, **kwargs):
    if 'stdout' not in kwargs:
        kwargs['stdout'] = PIPE

    if 'stderr' not in kwargs:
        kwargs['stderr'] = PIPE

    process = Popen(cmd, *args, **kwargs)
    stdout, stderr = process.communicate()

    if process.returncode:
        output = ""
        if stdout:
            output += stdout
        if stderr:
            output += stderr
        raise CalledProcessError(process.returncode, cmd, output)
    return 0


def docker_instance_command(cmd, server_hostname, instance_name):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        d = settings.DOKKU
        d.update({
            'instance_name': instance_name,
            'cmd': cmd
        })
        fabric.run('sudo docker ps -a | grep app/%(instance_name)s:latest | awk \'{ print $1 } \' | xargs sudo docker %(cmd)s' % d)

start = lambda server_hostname, instance_name: docker_instance_command('start', server_hostname, instance_name)
stop = lambda server_hostname, instance_name: docker_instance_command('stop', server_hostname, instance_name)
restart = lambda server_hostname, instance_name: docker_instance_command('restart', server_hostname, instance_name)


def delete(server_hostname, instance_name):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        d = settings.DOKKU.copy()
        d.update({
            'instance_name': instance_name
        })
        fabric.run('sudo docker ps | grep app/%(instance_name)s:latest | awk \'{ print $1 } \' | xargs sudo docker kill' % d)
        fabric.run('sudo docker rmi app/%(instance_name)s' % d)
        fabric.run('sudo rm -rf /home/%(GIT_USER)s/%(instance_name)s/' % d)


def update_environment(server_hostname, instance_name, env_pairs):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        d = settings.DOKKU.copy()
        d.update({
            'instance_name': instance_name
        })
        env_file_content = "\n".join([u"export %s='%s'" % (key, value) for key, value in env_pairs])
        put(StringIO.StringIO(env_file_content), '/home/%(GIT_USER)s/%(instance_name)s/ENV' % d, use_sudo=True)


def deploy_revision(deployment_pk, revision_pk, async=True):
    from dokku_controller.models import Revision, Deployment
    if async:
        q = Queue('default', connection=redis_connection)
        q.enqueue_call(deploy_revision, args=(deployment_pk, revision_pk, False,), timeout=3000)
    else:
        revision = Revision.objects.get(pk=revision_pk)
        deployment = Deployment.objects.get(pk=deployment_pk)
        deployment.status = "deploying"
        deployment.revision = revision
        deployment.save()
        docker_image_name = "%s/dokcon/%s:v%s" % (settings.DOCKER_IMAGE_SERVER_URL, deployment.app.name, revision.revision_number)
        process_types = ['web']
        try:
            if revision.docker_image_name and settings.DOCKER_IMAGE_SERVER_URL:
                with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], deployment.host.hostname)):
                    fabric.run('sudo docker pull %s' % docker_image_name)
                    for process_type in process_types:
                        fabric.run('sudo docker run -d -p 5000 -e PORT=5000 %s /bin/bash -c "/start %s"' % (docker_image_name, process_type))
            else:
                with TemporaryDirectory() as dirname:
                    check_call(["cp", revision.compressed_archive.path, os.path.join(dirname, 'app.tar.gz')])
                    check_call(["tar", "-xf", "app.tar.gz"], cwd=dirname)
                    check_call(["rm", "app.tar.gz"], cwd=dirname)
                    check_call(["git", "init"], cwd=dirname)
                    check_call(["git", "add", "."], cwd=dirname)
                    check_call(["git", "commit", "-am", "'initial'"], cwd=dirname)
                    check_call(["git", "push", "%s@%s:%s" % (settings.DOKKU['GIT_USER'], deployment.host.hostname, deployment.app.name), "master", "--force"], cwd=dirname)
                    if settings.DOCKER_IMAGE_SERVER_URL:
                        with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], deployment.host.hostname)):
                            # Tag the result from dokku with name and version
                            fabric.run('sudo docker tag app/%(app_name)s %(docker_image_name)s' % {
                               'image_url': settings.DOCKER_IMAGE_SERVER_URL,
                               'app_name': deployment.app.name,
                               'revision': revision.revision_number,
                               'docker_image_name': docker_image_name
                            })
                            # Push it to the image server
                            fabric.run('sudo docker push %s' % docker_image_name)
                            # Kill the dokku instance, to avoid inconsistencies. In this way, every instance is the one from the image server
                            fabric.run('sudo docker ps | grep app/%s:latest | awk \'{ print $1 } \' | xargs sudo docker kill' % deployment.app.name)
                            # Remove the dokku original image
                            fabric.run('sudo docker rmi app/%s' % deployment.app.name)
                            # Kill any previously running processes with the same revision number (shouldn't commonly happen)
                            fabric.run('sudo docker ps | grep "dokcon/app-%s:" | grep v%s | awk \'{ print $1 } \' | xargs sudo docker kill' % (deployment.app.name, revision.revision_number))
                            # Run the new process from the new image
                            for process_type in process_types:
                                fabric.run('sudo docker run -d -p 5000 -e PORT=5000 %s /bin/bash -c "/start %s"' % (docker_image_name, process_type))
                            # Clean up, by calling killing and removing all non-current images
                            fabric.run('sudo docker ps | grep "dokcon/app-%s:" | grep -v v%s | awk \'{ print $1 } \' | xargs sudo docker kill' % (deployment.app.name, revision.revision_number))
                            fabric.run('sudo docker images | grep "dokcon/app-%s " | grep -v v%s | awk \'{ print $3 } \' | xargs sudo docker rmi' % (deployment.app.name, revision.revision_number))
                        revision.docker_image_name = docker_image_name
                        revision.save()
            deployment.status = "deployed_success"
            deployment.error_message = "Success!"
        except CalledProcessError as e:
            deployment.status = "deployed_error"
            deployment.error_message = e.output
        except SystemExit as e:
            deployment.status = "deployed_error"
            deployment.error_message = traceback.format_exc()
        except Exception as e:
            deployment.status = "deployed_error"
            deployment.error_message = traceback.format_exc()
        finally:
            deployment.save()


def get_new_deployment_server(app):
    from dokku_controller.models import Host
    hosts = Host.objects.all().annotate(num_deployments=Count('deployment'))
    return min(hosts, key=lambda itm: itm.num_deployments)


def update_load_balancer_config(app_ids=None):
    from dokku_controller.models import App
    if not app_ids:
        apps = App.objects.all()
    else:
        apps = App.objects.filter(pk__in=app_ids)
    for app in apps:
        lb_config = [app.name]
        if app.paused:
            lb_config.append("paused")
        else:
            for deployment in app.deployment_set.filter(last_update__gt=now() - datetime.timedelta(minutes=5)):
                lb_config.append(deployment.endpoint)
        default_domain = ["%s.%s" % (app.name, settings.BASE_DOMAIN)]
        for domain in [domain.domain_name for domain in app.domain_set.all()] + default_domain:
            key = ("frontend:%s" % domain).lower()
            existing_config = redis_connection.lrange(key, 0, -1)
            if len(existing_config) == 0:
                redis_connection.rpush(key, *lb_config)
            elif not existing_config == lb_config and lb_config:
                redis_connection.ltrim(key, 1, 0)
                redis_connection.rpush(key, *lb_config)
            else:
                # Everything is up to date
                pass


def scan_host_key(hostname, async=True):
    if async:
        q = Queue('default', connection=redis_connection)
        q.enqueue_call(scan_host_key, args=(hostname, False))
    else:
        with open(os.path.expanduser("~/.ssh/known_hosts"), "a+") as out:
            check_call(['ssh-keyscan', hostname], stdout=out)