import StringIO
import fabric.api as fabric
from django.conf import settings
from fabric.operations import put

try:
    from shlex import quote  # Python 3.3+
except ImportError:
    from pipes import quote # Python 2.7-


def restart(server_hostname, instance_name):
    with fabric.settings(host_string='%s@%s' % (settings.DOKKU['SSH_USER'], server_hostname)):
        d = settings.DOKKU
        d.update({
            'instance_name': instance_name
        })
        fabric.run('sudo docker ps | grep app/%(instance_name)s:latest | awk \'{ print $1 } \' | xargs sudo docker restart' % d)


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