import StringIO
from subprocess import check_call as _check_call
import datetime
from django.db.models import Count
from dokku_controller.models import App
import fabric.api as fabric
from django.conf import settings
from fabric.operations import put, os
from rq import Queue
import time
from dokku_controller.utils import TemporaryDirectory
from project.redis_connection import connection as redis_connection
import logging
from django.utils.timezone import now

logging.basicConfig(
    format='%(asctime)s,%(msecs)05.1f (%(funcName)s) %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def check_call(cmd, *args, **kwargs):
    logging.debug(cmd)
    return _check_call(cmd, *args, **kwargs)


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
        d = settings.DOKKU
        d.update({
            'instance_name': instance_name
        })
        fabric.run('sudo docker ps | grep app/%(instance_name)s:latest | awk \'{ print $1 } \' | xargs sudo docker kill' % d)
        fabric.run('sudo docker rmi app/%(instance_name)s' % d)
        fabric.run('sudo rm -rf /home/%(GIT_USER)s/%(instance_name)s/' % d)


def update_environment(server_hostname, instance_name, env_pairs):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        d = settings.DOKKU
        d.update({
            'instance_name': instance_name
        })
        env_file_content = "\n".join([u"export %s='%s'" % (key, value) for key, value in env_pairs])
        put(StringIO.StringIO(env_file_content), '/home/%(GIT_USER)s/%(instance_name)s/ENV' % d, use_sudo=True)


def deploy_revision(server_hostname, instance_name, revision_number, revision_file_path, async=True):
    if async:
        q = Queue('default', connection=redis_connection)
        q.enqueue(deploy_revision, server_hostname, instance_name, revision_number, revision_file_path, False)
    else:
        with TemporaryDirectory() as dirname:
            check_call(["cp", revision_file_path, os.path.join(dirname, 'app.tar.gz')])
            check_call(["tar", "-xf", "app.tar.gz"], cwd=dirname)
            check_call(["rm", "app.tar.gz"], cwd=dirname)
            check_call(["git", "init"], cwd=dirname)
            check_call(["git", "add", "."], cwd=dirname)
            check_call(["git", "commit", "-am", "'initial'"], cwd=dirname)
            check_call(["git", "push", "git@%s:%s" % (server_hostname, instance_name), "master", "--force"], cwd=dirname)


def get_new_deployment_server(app):
    from dokku_controller.models import Host
    hosts = Host.objects.all().annotate(num_deployments=Count('deployment'))
    return min(hosts, key=lambda itm: itm.num_deployments)


def update_load_balancer_config(app_ids=None):
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
            key = "frontend:%s" % domain
            existing_config = redis_connection.lrange(key, 0, -1)
            if len(existing_config) == 0:
                redis_connection.rpush(key, *lb_config)
            elif not existing_config == lb_config:
                redis_connection.ltrim(key, 1, 0)
                redis_connection.rpush(key, *lb_config)
            else:
                # Everything is up to date
                pass