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
    print("❌ Error: LABEL_STUDIO_URL y LABEL_STUDIO_LEGACY_API_KEY deben estar definidos en .env")
    sys.exit(1)

# Instancia cliente
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_LEGACY_API_KEY)

# Cargar configuración de proyectos
try:
    with open(PROJECTS_JSON_PATH, 'r', encoding='utf-8') as f:
        projects_config = json.load(f)
except Exception as e:
    print(f"❌ Error al abrir {PROJECTS_JSON_PATH}: {e}")
    sys.exit(1)

# Obtener proyectos existentes
try:
    existing_projects = client.projects.list()
    existing_projects_map = {p.title: p for p in existing_projects}
except Exception as e:
    print(f"❌ Error obteniendo proyectos existentes: {e}")
    sys.exit(1)

print("🔍 Proyectos definidos en projects_index.json:")
indexed_projects = []
for idx, (project_title, project_info) in enumerate(projects_config.items()):
    indexed_projects.append((project_title, project_info))
    status = "Existe" if project_title in existing_projects_map else "No existe"
    print(f"{idx + 1}. {project_title} ({status})")

if not indexed_projects:
    print("⚠️ No se encontraron proyectos definidos en projects_index.json.")
    sys.exit(0)

# Seleccionar proyecto
while True:
    try:
        choice = int(input("\nSelecciona el número del proyecto: "))
        if 1 <= choice <= len(indexed_projects):
            selected_project_title, selected_project_info = indexed_projects[choice - 1]
            break
        else:
            print("❌ Número inválido. Por favor, introduce un número dentro del rango.")
    except ValueError:
        print("❌ Entrada inválida. Por favor, introduce un número.")

if selected_project_title not in existing_projects_map:
    print(f"❌ El proyecto '{selected_project_title}' no existe en Label Studio. Por favor, créalo primero.")
    sys.exit(1)

project_id = existing_projects_map[selected_project_title].id
data_source = selected_project_info.get("data_source")

if not data_source:
    print(f"❌ Error: El proyecto '{selected_project_title}' no tiene 'data_source' definida en projects_index.json.")
    sys.exit(1)

# Construir ruta del archivo
# Si data_source es una ruta absoluta, os.path.join la usará directamente, ignorando DATA_DIR.
# Se añade una advertencia para claridad.
if os.path.isabs(data_source):
    print(f"⚠️ Advertencia: 'data_source' '{data_source}' es una ruta absoluta. Se usará directamente.")
    data_file_path = data_source
else:
    data_file_path = os.path.join(DATA_DIR, data_source)

print(f"\n✅ Proyecto seleccionado: '{selected_project_title}' (ID: {project_id})")
print(f"ℹ️ Archivo de datos: '{data_file_path}'")

if not os.path.isfile(data_file_path):
    print(f"❌ Error: No se encontró el archivo de datos en la ruta especificada: {data_file_path}")
    sys.exit(1)

# Verificar si el proyecto tiene tasks existentes
try:
    tasks_pager = client.tasks.list(project=project_id, page_size=1)
    has_existing_tasks = next(iter(tasks_pager), None) is not None

    if has_existing_tasks:
        print("\n⚠️ ADVERTENCIA: Este proyecto ya tiene tasks existentes.")
        print("1. Crear nuevas tasks (puede duplicar datos)")
        print("2. Actualizar tasks existentes (requiere que el número de tasks coincida)")
        print("3. Cancelar")

        while True:
            try:
                action_choice = int(input("\nSelecciona una opción (1-3): "))
                if action_choice in [1, 2, 3]:
                    break
                else:
                    print("❌ Opción inválida. Por favor, selecciona 1, 2 o 3.")
            except ValueError:
                print("❌ Entrada inválida. Por favor, introduce un número.")
    else:
        action_choice = 1  # Crear nuevas por defecto si no hay tasks

except Exception as e:
    print(f"❌ Error verificando tasks existentes: {e}")
    action_choice = 1  # Por defecto crear nuevas

if action_choice == 3:
    print("ℹ️ Operación cancelada por el usuario.")
    sys.exit(0)

# Cargar datos
try:
    # Añadir una verificación explícita para archivos vacíos, que son una causa común de JSONDecodeError
    if os.path.getsize(data_file_path) == 0:
        print(f"❌ Error: El archivo de datos está vacío (0 bytes): {data_file_path}. No se pueden importar tasks.")
        sys.exit(1)

    with open(data_file_path, 'r', encoding='utf-8') as f:
        tasks_data = json.load(f)

    if not isinstance(tasks_data, list):
        print(f"❌ Error: El archivo de datos debe contener una lista de tasks (e.g., [...]): {data_file_path}")
        sys.exit(1)

    if not tasks_data: # Esto significa que es una lista vacía
        print(f"⚠️ Advertencia: El archivo de datos contiene una lista vacía de tasks: {data_file_path}. No hay tasks para procesar.")
        sys.exit(0) # Salir de forma controlada si la lista está vacía

    total_tasks = len(tasks_data)
    batch_size = max(1, total_tasks // 20)  # 5% del total

    print(f"\n📦 Total de tasks a procesar: {total_tasks}")
    print(f"ℹ️ Tamaño de lote para importación: {batch_size}")

    if action_choice == 1:
        # CREAR NUEVAS TASKS
        print("🚀 Creando nuevas tasks...")
        created_count = 0

        for i in range(0, total_tasks, batch_size):
            batch = tasks_data[i:i + batch_size]
            try:
                result = client.projects.import_tasks(id=project_id, request=batch)
                created_count += len(batch)
                progress = (created_count / total_tasks) * 100
                print(f"  ✅ Lote {i//batch_size + 1}: {len(batch)} tasks importadas. Progreso: {created_count}/{total_tasks} ({progress:.1f}%)")
            except Exception as e:
                print(f"  ❌ Error en lote {i//batch_size + 1}: {e}")
                # Continuar con el siguiente lote incluso si uno falla
                continue

        print(f"✅ Se crearon {created_count} nuevas tasks en el proyecto '{selected_project_title}'.")
        # Mostrar un resumen (head) de las primeras 2 tasks creadas
        print("\n📋 Ejemplo de tasks agregadas (head):")
        head_num = min(2, len(tasks_data))
        for idx in range(head_num):
            print(f"Task {idx+1}:")
            print(json.dumps(tasks_data[idx], ensure_ascii=False, indent=2))
            print('-'*32)

    elif action_choice == 2:
        # ACTUALIZAR TASKS EXISTENTES
        print("🔄 Actualizando tasks existentes...")

        # Obtener todas las tasks existentes
        existing_tasks = list(client.tasks.list(project=project_id))
        existing_tasks_map = {task.id: task for task in existing_tasks}

        print(f"🔍 Tasks existentes encontradas en Label Studio: {len(existing_tasks)}")

        if len(existing_tasks) != len(tasks_data):
            print(f"⚠️ ADVERTENCIA: El número de tasks en el archivo ({len(tasks_data)}) no coincide con las existentes en Label Studio ({len(existing_tasks)}).")
            confirm = input("¿Continuar con la actualización (puede llevar a errores si las IDs no coinciden)? (s/N): ").strip().lower()
            if confirm != 's':
                print("ℹ️ Operación de actualización cancelada por el usuario.")
                sys.exit(0)

        updated_count = 0
        # La lógica actual asume una correspondencia 1:1 y ordenada entre tasks_data y existing_tasks.
        # Si tasks_data no contiene IDs de tasks para mapear, esta lógica es frágil.
        existing_task_ids = list(existing_tasks_map.keys())

        for i in range(0, total_tasks, batch_size):
            batch = tasks_data[i:i + batch_size]

            for task_index, task_data in enumerate(batch):
                if (i + task_index) < len(existing_task_ids):
                    task_id_to_update = existing_task_ids[i + task_index]
                    try:
                        # Actualizar task existente
                        client.tasks.update(id=task_id_to_update, data=task_data)
                        updated_count += 1
                    except Exception as e:
                        print(f"  ❌ Error actualizando task {task_id_to_update}: {e}")
                        continue
                else:
                    print(f"  ⚠️ Advertencia: No hay task existente correspondiente para el índice {i + task_index}. Saltando.")
                    continue

            progress = (min(i + batch_size, total_tasks) / total_tasks) * 100
            print(f"  ✅ Lote {i//batch_size + 1}: Progreso: {min(i + batch_size, total_tasks)}/{total_tasks} tasks ({progress:.1f}%)")

        print(f"✅ Se actualizaron {updated_count} tasks existentes en el proyecto '{selected_project_title}'.")
        # Mostrar un resumen (head) de las primeras 2 tasks del archivo
        print("\n📋 Ejemplo de tasks actualizadas (head):")
        head_num = min(2, len(tasks_data))
        for idx in range(head_num):
            print(f"Task {idx+1}:")
            print(json.dumps(tasks_data[idx], ensure_ascii=False, indent=2))
            print('-'*32)

except json.JSONDecodeError as e:
    error_message = str(e)
    if "Expecting value: line 1 column 1 (char 0)" in error_message:
        print(f"❌ Error: El archivo de datos '{data_file_path}' parece estar vacío o no contiene JSON válido al inicio.")
        print("   Por favor, verifica que el archivo no esté vacío y que su contenido sea un JSON bien formado.")
    else:
        print(f"❌ Error decodificando JSON en {data_file_path}: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error inesperado al procesar tasks: {e}")
    sys.exit(1)

print("🎉 Proceso completado!")