import os
import sys
import json
from dotenv import load_dotenv
from label_studio_sdk import LabelStudio

# Carga variables de entorno
load_dotenv()

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL')
LABEL_STUDIO_LEGACY_API_KEY = os.getenv('LABEL_STUDIO_LEGACY_API_KEY')

# Definir rutas base
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(BASE_DIR, 'data')
PROJECTS_DIR = os.path.join(BASE_DIR, 'projects')
PROJECTS_JSON_PATH = os.path.join(PROJECTS_DIR, 'projects_index.json')

if not LABEL_STUDIO_URL or not LABEL_STUDIO_LEGACY_API_KEY:
    print("Error: LABEL_STUDIO_URL y LABEL_STUDIO_LEGACY_API_KEY deben estar definidos en .env")
    sys.exit(1)

# Instancia cliente
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_LEGACY_API_KEY)

# Cargar configuración de proyectos
try:
    with open(PROJECTS_JSON_PATH, 'r', encoding='utf-8') as f:
        projects_config = json.load(f)
except Exception as e:
    print(f"Error al abrir {PROJECTS_JSON_PATH}: {e}")
    sys.exit(1)

# Obtener proyectos existentes
try:
    existing_projects = client.projects.list()
    existing_projects_map = {p.title: p for p in existing_projects}
except Exception as e:
    print(f"Error obteniendo proyectos existentes: {e}")
    sys.exit(1)

print("Proyectos definidos en projects_index.json:")
indexed_projects = []
for idx, (project_title, project_info) in enumerate(projects_config.items()):
    indexed_projects.append((project_title, project_info))
    status = "Existe" if project_title in existing_projects_map else "No existe"
    print(f"{idx + 1}. {project_title} ({status})")

if not indexed_projects:
    print("No se encontraron proyectos definidos.")
    sys.exit(0)

# Seleccionar proyecto
while True:
    try:
        choice = int(input("\nSelecciona el numero del proyecto: "))
        if 1 <= choice <= len(indexed_projects):
            selected_project_title, selected_project_info = indexed_projects[choice - 1]
            break
        else:
            print("Numero invalido.")
    except ValueError:
        print("Entrada invalida.")

if selected_project_title not in existing_projects_map:
    print(f"El proyecto '{selected_project_title}' no existe en Label Studio.")
    sys.exit(1)

project_id = existing_projects_map[selected_project_title].id
data_source = selected_project_info.get("data_source")

if not data_source:
    print(f"El proyecto no tiene 'data_source' definida.")
    sys.exit(0)

# Construir ruta del archivo
data_file_path = os.path.join(DATA_DIR, data_source)

print(f"\nProyecto seleccionado: '{selected_project_title}' (ID: {project_id})")
print(f"Archivo de datos: '{data_file_path}'")

if not os.path.isfile(data_file_path):
    print(f"Error: No se encontro el archivo de datos")
    sys.exit(1)

# Verificar si el proyecto tiene tasks existentes
try:
    tasks_pager = client.tasks.list(project=project_id, page_size=1)
    has_existing_tasks = next(iter(tasks_pager), None) is not None
    
    if has_existing_tasks:
        print("\nADVERTENCIA: Este proyecto ya tiene tasks existentes.")
        print("1. Crear nuevas tasks (puede duplicar datos)")
        print("2. Actualizar tasks existentes")
        print("3. Cancelar")
        
        while True:
            try:
                action_choice = int(input("\nSelecciona una opcion (1-3): "))
                if action_choice in [1, 2, 3]:
                    break
                else:
                    print("Opcion invalida.")
            except ValueError:
                print("Entrada invalida.")
    else:
        action_choice = 1  # Crear nuevas por defecto si no hay tasks
        
except Exception as e:
    print(f"Error verificando tasks existentes: {e}")
    action_choice = 1  # Por defecto crear nuevas

if action_choice == 3:
    print("Operacion cancelada.")
    sys.exit(0)

# Cargar datos
try:
    with open(data_file_path, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)
    
    if not isinstance(tasks_data, list) or not tasks_data:
        print("El archivo JSON esta vacio o no es una lista de tasks.")
        sys.exit(0)

    total_tasks = len(tasks_data)
    batch_size = max(1, total_tasks // 20)  # 5% del total
    
    print(f"\nTotal de tasks a procesar: {total_tasks}")
    print(f"Tamaño de lote: {batch_size}")

    if action_choice == 1:
        # CREAR NUEVAS TASKS
        print("Creando nuevas tasks...")
        created_count = 0
        
        for i in range(0, total_tasks, batch_size):
            batch = tasks_data[i:i + batch_size]
            try:
                result = client.projects.import_tasks(id=project_id, request=batch)
                created_count += len(batch)
                progress = (created_count / total_tasks) * 100
                print(f"Progreso: {created_count}/{total_tasks} tasks ({progress:.1f}%)")
            except Exception as e:
                print(f"Error en lote {i//batch_size + 1}: {e}")
                continue
        
        print(f"Se crearon {created_count} nuevas tasks.")
        
    elif action_choice == 2:
        # ACTUALIZAR TASKS EXISTENTES
        print("Actualizando tasks existentes...")
        
        # Obtener todas las tasks existentes
        existing_tasks = list(client.tasks.list(project=project_id))
        existing_tasks_map = {task.id: task for task in existing_tasks}
        
        print(f"Tasks existentes encontradas: {len(existing_tasks)}")
        
        if len(existing_tasks) != len(tasks_data):
            print("ADVERTENCIA: El numero de tasks en el archivo no coincide con las existentes.")
            confirm = input("¿Continuar? (s/N): ").strip().lower()
            if confirm != 's':
                print("Operacion cancelada.")
                sys.exit(0)
        
        updated_count = 0
        for i in range(0, total_tasks, batch_size):
            batch = tasks_data[i:i + batch_size]
            
            for task_index, task_data in enumerate(batch):
                task_id = list(existing_tasks_map.keys())[i + task_index]
                try:
                    # Actualizar task existente
                    client.tasks.update(id=task_id, data=task_data)
                    updated_count += 1
                except Exception as e:
                    print(f"Error actualizando task {task_id}: {e}")
                    continue
            
            progress = (min(i + batch_size, total_tasks) / total_tasks) * 100
            print(f"Progreso: {min(i + batch_size, total_tasks)}/{total_tasks} tasks ({progress:.1f}%)")
        
        print(f"Se actualizaron {updated_count} tasks existentes.")
        
except Exception as e:
    print(f"Error procesando tasks: {e}")
    sys.exit(1)

print("Proceso completado.")