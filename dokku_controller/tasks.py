import StringIO
from subprocess import check_call as _check_call
from django.db.models import Count
import fabric.api as fabric
from django.conf import settings
from fabric.operations import put, os
from rq import Queue
import time
from dokku_controller.utils import TemporaryDirectory
from project.redis_connection import connection as redis_connection
import logging

logging.basicConfig(
    format='%(asctime)s,%(msecs)05.1f (%(funcName)s) %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.DEBUG)


def check_call(cmd, *args, **kwargs):
    logging.debug(cmd)
    return _check_call(cmd, *args, **kwargs)


def docker(cmd, server_hostname, instance_name):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        fabric.run('sudo docker %s app/%s' % (cmd, instance_name))


def docker_running_instance_command(cmd, server_hostname, instance_name):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        d = settings.DOKKU
        d.update({
            'instance_name': instance_name,
            'cmd': cmd
        })
        fabric.run('sudo docker ps | grep app/%(instance_name)s:latest | awk \'{ print $1 } \' | xargs sudo docker %(cmd)s' % d)

start = lambda server_hostname, instance_name: docker('start', server_hostname, instance_name)
stop = lambda server_hostname, instance_name: docker_running_instance_command('stop', server_hostname, instance_name)
restart = lambda server_hostname, instance_name: docker_running_instance_command('restart', server_hostname, instance_name)

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