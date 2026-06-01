#!/bin/bash

echo "Iniciando migraciones..."
python manage.py migrate --noinput

echo "Migraciones completadas."

echo "Iniciando servidor..."
exec gunicorn config.wsgi:application --bind 0.0.0.0:$PORT