from time import sleep
import json
import logging
import datetime
from django.core.management import BaseCommand
from dokku_controller.models import Deployment, Host, App

logging.basicConfig(
    format='%(asctime)s,%(msecs)05.1f (%(funcName)s) %(message)s',
    datefmt='%H:%M:%S')
log = logging.getLogger()
log.setLevel(logging.INFO)
import gevent
import socket as python_socket
from gevent import socket
from project.redis_connection import connection as redis_connection
import redis
import redis.connection
redis.connection.socket = socket


hostname = python_socket.gethostname()


def clean_deployments():
    while True:
        # Loop over docker instances that starts with app/ and return endpoint and optionally HTTP status
        for deployment in Deployment.objects.filter(last_update__lte=datetime.datetime.now() - datetime.timedelta(minutes=5)):
            logging.info(deployment)
            #redis_connection.publish("app_status", json.dumps(app))
        gevent.sleep(60)


def listen_for_requests():
    pubsub_connection = redis_connection.pubsub()
    pubsub_connection.subscribe(['app_announce'])
    for itm in pubsub_connection.listen():
        if itm['type'] == 'message':
            data = json.loads(itm['data'])
            host, created = Host.objects.get_or_create(hostname=data.keys()[0])
            for app in data.values()[0]:
                app, created = App.objects.get_or_create(name=app)
                deployment_qs = Deployment.objects.filter(app=app, host=host)
                if deployment_qs.exists():
                    deployment = deployment_qs.get()
                else:
                    deployment = Deployment(app=app, host=host)
                deployment.last_update = datetime.datetime.now()
                deployment.save()
        logging.info(itm)

class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        clean_event = gevent.spawn(clean_deployments)
        listen_for_requests_even = gevent.spawn(listen_for_requests)
        gevent.joinall([clean_event, listen_for_requests_even])