web: gunicorn project.wsgi:application
worker: python manage.py rqworker
listener: python manage.py listen