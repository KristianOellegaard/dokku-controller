from time import sleep
import json
import logging
import datetime
from django.core.management import BaseCommand
from dokku_controller.models import Deployment, Host, App
from django.conf import settings
from dokku_controller.tasks import update_load_balancer_config
import gevent
import socket as python_socket
from gevent import socket
from django.utils.timezone import now
from project.redis_connection import connection as redis_connection
import redis
import redis.connection
redis.connection.socket = socket

logging.basicConfig(
    format='%(asctime)s,%(msecs)05.1f (%(funcName)s) %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.INFO)


hostname = python_socket.gethostname()


def clean_deployments():
    while True:
        for deployment in Deployment.objects.filter(last_update__lte=now() - datetime.timedelta(minutes=5)):
            logging.warn(u"%s didn't check in for at least 5 min" % deployment)
        gevent.sleep(60)


def listen_for_requests():
    pubsub_connection = redis_connection.pubsub()
    pubsub_connection.subscribe(['app_announce'])
    for itm in pubsub_connection.listen():
        logging.info(itm)
        if itm['type'] == 'message':
            data = json.loads(itm['data'])
            host, created = Host.objects.get_or_create(hostname=data.keys()[0])
            for app, port in data.values()[0]:
                app, created = App.objects.get_or_create(name=app)
                deployment_qs = Deployment.objects.filter(app=app, host=host)
                if deployment_qs.exists():
                    deployment = deployment_qs.get()
                else:
                    deployment = Deployment(app=app, host=host)
                deployment.last_update = datetime.datetime.now()
                deployment.endpoint = "http://%s:%s/" % (host.hostname, port)
                deployment.save()


def update_load_balancer():
    while True:
        update_load_balancer_config()
        gevent.sleep(25)


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        clean_event = gevent.spawn(clean_deployments)
        listen_for_requests_event = gevent.spawn(listen_for_requests)
        load_balancer_event = gevent.spawn(update_load_balancer)
        gevent.joinall([clean_event, listen_for_requests_event, load_balancer_event])