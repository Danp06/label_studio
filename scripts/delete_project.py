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

print(f"Se encontraron {project_count} proyectos en Label Studio:")

for idx, project in enumerate(existing_projects):
    print(f"{idx + 1}. {project.title} (ID: {project.id})")

# Opciones de eliminación
print("\nOpciones de eliminacion:")
print("1. Eliminar TODOS los proyectos")
print("2. Eliminar proyecto especifico")
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
    # ELIMINAR TODOS LOS PROYECTOS
    print(f"\nADVERTENCIA CRITICA: Esta accion eliminara TODOS los {project_count} proyectos.")
    print("Se perderan TODOS los datos, tasks, anotaciones y configuraciones.")
    print("Esta accion NO se puede deshacer.")
    
    confirm = input("¿Estas absolutamente seguro? (escribe 'ELIMINAR-TODO' para confirmar): ").strip()
    
    if confirm != 'ELIMINAR-TODO':
        print("Operacion cancelada.")
        sys.exit(0)
    
    try:
        deleted_count = 0
        errors = []
        
        print(f"\nEliminando {project_count} proyectos...")
        
        for project in existing_projects:
            try:
                client.projects.delete(id=project.id)
                deleted_count += 1
                print(f"Proyecto '{project.title}' eliminado")
            except Exception as e:
                errors.append(f"Proyecto '{project.title}': {e}")
                print(f"Error eliminando proyecto '{project.title}': {e}")
        
        print(f"\nEliminacion completada: {deleted_count} proyectos eliminados exitosamente.")
        
        if errors:
            print(f"Se encontraron {len(errors)} errores durante la eliminacion.")
                
    except Exception as e:
        print(f"Error durante la eliminacion: {e}")

elif action_choice == 2:
    # ELIMINAR PROYECTO ESPECIFICO
    print("\nLista de proyectos:")
    for idx, project in enumerate(existing_projects):
        print(f"{idx + 1}. {project.title} (ID: {project.id})")
    print("0. Ninguno / Cancelar")

    while True:
        try:
            choice = int(input("\nSelecciona el numero del proyecto a eliminar (o 0 para cancelar): "))
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

    print(f"\nProyecto seleccionado: '{selected_project.title}' (ID: {selected_project.id})")

    # Confirmación de eliminación
    print(f"\nADVERTENCIA: Esta accion eliminara el proyecto '{selected_project.title}' y TODOS sus datos.")
    print("Esta accion NO se puede deshacer.")

    confirm = input("¿Estas seguro que deseas continuar? (escribe 'ELIMINAR' para confirmar): ").strip()

    if confirm != 'ELIMINAR':
        print("Operacion cancelada.")
        sys.exit(0)

    try:
        print("Eliminando proyecto...")
        client.projects.delete(id=selected_project.id)
        print(f"Proyecto '{selected_project.title}' eliminado exitosamente.")
    except Exception as e:
        print(f"Error eliminando proyecto: {e}")