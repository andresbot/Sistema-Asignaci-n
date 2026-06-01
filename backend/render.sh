#!/bin/bash

echo "Iniciando migraciones..."
python manage.py migrate --noinput

echo "Creando superusuario por defecto si no existe..."
# Crea un usuario admin 
python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print("Superusuario 'admin' creado con éxito.")
else:
    print("El superusuario 'admin' ya existe.")
EOF

echo "Iniciando servidor..."