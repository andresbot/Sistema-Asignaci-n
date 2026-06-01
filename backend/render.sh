#!/bin/bash

echo "Iniciando migraciones..."
python manage.py migrate --noinput

echo "Migraciones completadas."

echo "Creando superusuario si no existe..."
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superusuario creado.")
else:
    print("El superusuario ya existe.")
EOF

echo "Iniciando servidor Gunicorn..."
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT