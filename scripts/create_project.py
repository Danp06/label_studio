#!/usr/bin/env python3

import os
import sys
import json
from dotenv import load_dotenv
from label_studio_sdk import LabelStudio

# Carga variables de entorno desde el .env
load_dotenv()

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL')
LABEL_STUDIO_LEGACY_API_KEY = os.getenv('LABEL_STUDIO_LEGACY_API_KEY')

# Calcular rutas relativas correctamente desde el directorio base del proyecto
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
PROJECTS_JSON_PATH = os.path.join(PROJECTS_DIR, 'projects_index.json')

if not LABEL_STUDIO_URL or not LABEL_STUDIO_LEGACY_API_KEY:
    print("❌ Debes definir LABEL_STUDIO_URL y LABEL_STUDIO_LEGACY_API_KEY en tu archivo .env")
    sys.exit(1)

# Instancia cliente de Label Studio SDK
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_LEGACY_API_KEY)

# Cargar proyectos desde projects.json
try:
    with open(PROJECTS_JSON_PATH, 'r', encoding='utf-8') as f:
        projects_dict = json.load(f)
except Exception as e:
    print(f"❌ Error al abrir {PROJECTS_JSON_PATH}: {e}")
    sys.exit(1)

# Obtener todos los títulos de proyectos ya existentes en Label Studio
try:
    existing_projects = client.projects.list()
    existing_titles = set(p.title for p in existing_projects)
except Exception as e:
    print(f"❌ Error obteniendo la lista de proyectos existentes: {e}")
    sys.exit(1)

for project_id, project_info in projects_dict.items():
    # project_info ahora es un dict esperado con "schema" y "data_source"
    if not isinstance(project_info, dict):
        print(f"❌ El valor para '{project_id}' debería ser un objeto JSON con las llaves 'schema' y 'data_source'.")
        continue

    schema_file = project_info.get("schema")
    if not schema_file:
        print(f"❌ El proyecto '{project_id}' no tiene la clave 'schema' definida.")
        continue

    # Verificar si el título ya existe
    if project_id in existing_titles:
        print(f"⚠️ Ya existe un proyecto en Label Studio con el nombre '{project_id}'. Cambia el nombre en el archivo JSON '{PROJECTS_JSON_PATH}' si deseas crear un nuevo proyecto.")
        continue

    schema_path = os.path.join(PROJECTS_DIR, schema_file)
    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            label_config = f.read()
    except Exception as e:
        print(f"❌ No se pudo leer el schema '{schema_file}' para el proyecto '{project_id}': {e}")
        continue

    try:
        project = client.projects.create(
            title=project_id,
            label_config=label_config
        )
        print(f"✅ Proyecto '{project_id}' creado exitosamente. Project ID: {project.id}")
        existing_titles.add(project_id)
    except Exception as e:
        print(f"❌ Error creando el proyecto '{project_id}': {e}")
        continue

    # Después de crear exitosamente el proyecto, importar los tasks al proyecto con la data de data_source si está presente
    data_source = project_info.get("data_source")
    if not data_source:
        print(f"⚠️ Proyecto '{project_id}' no tiene definida la clave 'data_source', no se importarán tasks automáticamente.")
        continue

    data_file_path = os.path.join(PROJECTS_DIR, "..", "data", data_source)
    if not os.path.isfile(data_file_path):
        print(f"❌ No se encontró el archivo de datos '{data_file_path}' para el proyecto '{project_id}'.")
        continue

    try:
        # Asumimos que el archivo de datos es un JSON con tasks (lista de diccionarios)
        with open(data_file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        if not isinstance(tasks, list) or not tasks:
            print(f"⚠️ El archivo JSON de datos '{data_file_path}' está vacío o no es una lista para el proyecto '{project_id}'.")
            continue

        result = client.projects.import_tasks(
            id=project.id,
            request=tasks
        )
        print(f"✅ Se importaron {len(tasks)} tasks al proyecto '{project_id}' (ID: {project.id}).")
    except Exception as e:
        print(f"❌ Error importando tasks al proyecto '{project_id}': {e}")
