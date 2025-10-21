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
DATA_DIR = os.path.join(BASE_DIR, 'data')  # Ruta corregida para datos
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

print(f"🔍 Encontrados {len(projects_dict)} proyectos en el índice")
print(f"🔍 Existen {len(existing_titles)} proyectos en Label Studio")

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
        print(f"⚠️ Ya existe un proyecto en Label Studio con el nombre '{project_id}'. Saltando...")
        continue

    # Cargar y validar schema
    schema_path = os.path.join(PROJECTS_DIR, schema_file)
    if not os.path.isfile(schema_path):
        print(f"❌ No se encuentra el archivo schema: {schema_path}")
        continue

    try:
        with open(schema_path, 'r', encoding='utf-8') as f:
            label_config = f.read()
        print(f"✅ Schema cargado: {schema_file}")
    except Exception as e:
        print(f"❌ No se pudo leer el schema '{schema_file}' para el proyecto '{project_id}': {e}")
        continue

    # Crear proyecto en Label Studio
    try:
        project = client.projects.create(
            title=project_id,
            label_config=label_config
        )
        print(f"✅ Proyecto '{project_id}' creado exitosamente. Project ID: {project.id}")
        existing_titles.add(project_id)  # Actualizar set local
    except Exception as e:
        print(f"❌ Error creando el proyecto '{project_id}': {e}")
        continue

    # Después de crear exitosamente el proyecto, importar los tasks
    data_source = project_info.get("data_source")
    if not data_source:
        print(f"⚠️ Proyecto '{project_id}' no tiene definida la clave 'data_source', no se importarán tasks.")
        continue

    # CORRECCIÓN PRINCIPAL: Usar DATA_DIR en lugar de ruta relativa compleja
    data_file_path = os.path.join(DATA_DIR, data_source)
    
    if not os.path.isfile(data_file_path):
        print(f"❌ No se encontró el archivo de datos: {data_file_path}")
        continue

    try:
        # Cargar datos
        with open(data_file_path, 'r', encoding='utf-8') as f:
            tasks = json.load(f)
        
        if not isinstance(tasks, list):
            print(f"❌ El archivo de datos debe contener una lista de tasks: {data_file_path}")
            continue

        if not tasks:
            print(f"⚠️ El archivo de datos está vacío: {data_file_path}")
            continue

        print(f"📦 Importando {len(tasks)} tasks al proyecto '{project_id}'...")

        # Importar en lotes de 5% de la cantidad total de tasks
        total_tasks = len(tasks)
        batch_size = max(1, total_tasks // 20)  # 5% del total, al menos 1

        imported_count = 0

        for i in range(0, total_tasks, batch_size):
            batch = tasks[i:i + batch_size]
            try:
                result = client.projects.import_tasks(
                    id=project.id,
                    request=batch
                )
                imported_count += len(batch)
                progress = (imported_count / total_tasks) * 100
                print(f"  ✅ Lote {i//batch_size + 1}: {len(batch)} tasks importadas. Progreso: {imported_count}/{total_tasks} ({progress:.1f}%)")
            except Exception as e:
                print(f"  ❌ Error en lote {i//batch_size + 1}: {e}")
                continue

        print(f"✅ Se importaron {imported_count}/{len(tasks)} tasks al proyecto '{project_id}'")
        
    except json.JSONDecodeError as e:
        print(f"❌ Error decodificando JSON en {data_file_path}: {e}")
    except Exception as e:
        print(f"❌ Error importando tasks al proyecto '{project_id}': {e}")

print("🎉 Proceso completado!")