from django.core.management import BaseCommand
import redis
from rq import Worker, Queue, Connection
from project.redis_connection import pool


class Command(BaseCommand):

    def handle(self, *args, **kwargs):
        listen = ['high', 'default', 'low']

        conn = redis.StrictRedis(connection_pool=pool)

        with Connection(conn):
            worker = Worker(map(Queue, listen))
            worker.work()