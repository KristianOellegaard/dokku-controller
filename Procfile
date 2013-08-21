web: python manage.py run_gunicorn -w ${WEB_PROCESSES:-4} -b 0.0.0.0:${PORT}
worker: python manage.py rqworker
listener: python manage.py listen