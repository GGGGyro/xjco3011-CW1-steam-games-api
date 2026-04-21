web: python manage.py migrate && python manage.py collectstatic --noinput && gunicorn steam_api.wsgi --bind 0.0.0.0:$PORT
