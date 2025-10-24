#!/usr/bin/env python3

import os
import sys
import time
from dotenv import load_dotenv
from label_studio_sdk import LabelStudio

# Carga variables de entorno desde el .env
load_dotenv()

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL')
LABEL_STUDIO_LEGACY_API_KEY = os.getenv('LABEL_STUDIO_LEGACY_API_KEY')

if not LABEL_STUDIO_URL or not LABEL_STUDIO_LEGACY_API_KEY:
    print("✗ Debes definir LABEL_STUDIO_URL y LABEL_STUDIO_LEGACY_API_KEY en tu archivo .env")
    sys.exit(1)

# Instancia cliente de Label Studio SDK
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_LEGACY_API_KEY)

# Lista de usuarios a crear desde variables de entorno
USERS_CONFIG = [
    {
        'email': os.getenv('TUTOR1_EMAIL'),
        'username': os.getenv('TUTOR1_USERNAME'), # Añadido username
        'first_name': os.getenv('TUTOR1_FIRST_NAME', ''),
        'last_name': os.getenv('TUTOR1_LAST_NAME', ''),
    },
    {
        'email': os.getenv('TUTOR2_EMAIL'),
        'username': os.getenv('TUTOR2_USERNAME'), # Añadido username
        'first_name': os.getenv('TUTOR2_FIRST_NAME', ''),
        'last_name': os.getenv('TUTOR2_LAST_NAME', ''),
    },
    {
        'email': os.getenv('TUTOR3_EMAIL'),
        'username': os.getenv('TUTOR3_USERNAME'), # Añadido username
        'first_name': os.getenv('TUTOR3_FIRST_NAME', ''),
        'last_name': os.getenv('TUTOR3_LAST_NAME', ''),
    },
    {
        'email': os.getenv('SOPORTE_EMAIL'),
        'username': os.getenv('SOPORTE_USERNAME'), # Añadido username
        'first_name': os.getenv('SOPORTE_FIRST_NAME', ''),
        'last_name': os.getenv('SOPORTE_LAST_NAME', ''),
    },
]

# Filtrar usuarios válidos (que tengan email y username definidos en .env)
users_to_create = [u for u in USERS_CONFIG if u.get('email') and u.get('username')]

if not users_to_create:
    print("✗ No hay usuarios válidos (email y username) definidos en el archivo .env")
    sys.exit(1)

print(f"📋 Encontrados {len(users_to_create)} usuarios en la configuración")

# Obtener todos los emails y usernames de usuarios ya existentes en Label Studio
try:
    existing_users = client.users.list()
    existing_emails = set(user.email for user in existing_users)
    existing_usernames = set(user.username for user in existing_users if user.username) # Recopilar usernames, asegurando que no sean None
except Exception as e:
    print(f"✗ Error obteniendo la lista de usuarios existentes: {e}")
    sys.exit(1)

print(f"📋 Existen {len(existing_emails)} usuarios en Label Studio (contando por email)")
print(f"📋 Existen {len(existing_usernames)} usuarios en Label Studio (contando por username)")

# Crear usuarios
created_count = 0
skipped_count = 0

for user_data in users_to_create:
    email = user_data.get('email')
    username = user_data.get('username') # Obtener el username
    
    # Verificar si el email o username ya existe
    if email in existing_emails:
        print(f"⚠️ Ya existe un usuario en Label Studio con el email '{email}'. Saltando...")
        skipped_count += 1
        continue
    if username in existing_usernames:
        print(f"⚠️ Ya existe un usuario en Label Studio con el username '{username}'. Saltando...")
        skipped_count += 1
        continue
    
    # Crear usuario usando el SDK
    try:
        new_user = client.users.create(
            email=email,
            username=username, # Pasar username al método create
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        print(f"✅ Usuario '{username}' (Email: '{email}') creado exitosamente. User ID: {new_user.id}")
        existing_emails.add(email)  # Actualizar set local de emails
        existing_usernames.add(username) # Actualizar set local de usernames
        created_count += 1
    except Exception as e:
        print(f"✗ Error creando el usuario '{username}' (Email: '{email}'): {e}")
        continue
    
    time.sleep(1)  # Pequeña pausa entre creaciones

print(f"\n🎉 Proceso completado!")
print(f"  ✅ Usuarios creados: {created_count}")
print(f"  ⚠️ Usuarios omitidos (ya existían por email o username): {skipped_count}")