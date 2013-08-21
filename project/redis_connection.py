import redis
from django.conf import settings

url = settings.REDIS_URL
pool = redis.ConnectionPool(host=url.hostname, port=url.port, db=0, password=url.password)
print "Connecting to redis", url.hostname
connection = redis.StrictRedis(connection_pool=pool)