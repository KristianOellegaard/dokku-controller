import fabric.api as fabric
from django.conf import settings


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