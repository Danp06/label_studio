import os
import sys
import json
from dotenv import load_dotenv
from label_studio_sdk import LabelStudio

# Carga variables de entorno
load_dotenv()

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL')
LABEL_STUDIO_LEGACY_API_KEY = os.getenv('LABEL_STUDIO_LEGACY_API_KEY')

if not LABEL_STUDIO_URL or not LABEL_STUDIO_LEGACY_API_KEY:
    print("Error: LABEL_STUDIO_URL y LABEL_STUDIO_LEGACY_API_KEY deben estar definidos en .env")
    sys.exit(1)

# Instancia cliente
client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=LABEL_STUDIO_LEGACY_API_KEY)

# Obtener TODOS los proyectos existentes en Label Studio
try:
    existing_projects = list(client.projects.list())
    project_count = len(existing_projects)
except Exception as e:
    print(f"Error obteniendo proyectos existentes: {e}")
    sys.exit(1)

if project_count == 0:
    print("No se encontraron proyectos existentes.")
    sys.exit(0)

print("Proyectos disponibles en Label Studio:")
for idx, project in enumerate(existing_projects):
    print(f"{idx + 1}. {project.title} (ID: {project.id})")
print("0. Ninguno / Cancelar")

# Seleccionar proyecto (ahora con opcion 0 para cancelar)
while True:
    try:
        choice = int(input("\nSelecciona el numero del proyecto (o 0 para cancelar): "))
        if choice == 0:
            print("Operacion cancelada.")
            sys.exit(0)
        elif 1 <= choice <= len(existing_projects):
            selected_project = existing_projects[choice - 1]
            break
        else:
            print("Numero invalido.")
    except ValueError:
        print("Entrada invalida.")

project_id = selected_project.id
project_title = selected_project.title

print(f"\nProyecto seleccionado: '{project_title}' (ID: {project_id})")

# Opciones de eliminación
print("\nOpciones de eliminacion:")
print("1. Eliminar TODAS las tasks del proyecto")
print("2. Eliminar tasks especificas por ID")
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

if action_choice == 3:
    print("Operacion cancelada.")
    sys.exit(0)

if action_choice == 1:
    # ELIMINAR TODAS LAS TASKS - DIRECTO SIN CONTAR
    print(f"\nADVERTENCIA: Esta accion eliminara TODAS las tasks del proyecto.")
    print("Esta accion NO se puede deshacer.")
    
    confirm = input("¿Estas seguro que deseas continuar? (escribe 'ELIMINAR' para confirmar): ").strip()
    
    if confirm != 'ELIMINAR':
        print("Operacion cancelada.")
        sys.exit(0)
    
    try:
        print("Eliminando todas las tasks...")
        client.tasks.delete_all_tasks(id=project_id)
        print("Todas las tasks han sido eliminadas del proyecto.")
    except Exception as e:
        print(f"Error eliminando tasks: {e}")

elif action_choice == 2:
    # ELIMINAR TASKS ESPECIFICAS
    print("\nIngresa los IDs de las tasks a eliminar (separados por comas):")
    task_ids_input = input("IDs: ").strip()
    
    if not task_ids_input:
        print("No se ingresaron IDs.")
        sys.exit(0)
    
    try:
        task_ids = [tid.strip() for tid in task_ids_input.split(',')]
        
        confirm = input("¿Confirmar eliminacion? (s/N): ").strip().lower()
        
        if confirm != 's':
            print("Operacion cancelada.")
            sys.exit(0)
        
        deleted_count = 0
        errors = []
        
        for task_id in task_ids:
            try:
                client.tasks.delete(id=task_id)
                deleted_count += 1
                print(f"Task {task_id} eliminada")
            except Exception as e:
                errors.append(f"Task {task_id}: {e}")
                print(f"Error eliminando task {task_id}: {e}")
        
        print(f"Eliminacion completada.")
        
        if errors:
            print(f"Se encontraron {len(errors)} errores durante la eliminacion.")
                
    except Exception as e:
        print(f"Error procesando IDs: {e}")