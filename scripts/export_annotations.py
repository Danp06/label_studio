#!/usr/bin/env python3

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from label_studio_sdk import LabelStudio
import subprocess

load_dotenv(dotenv_path='/.env')

LABEL_STUDIO_URL = os.getenv('LABEL_STUDIO_URL', 'http://localhost:8080')
LABEL_STUDIO_LEGACY_API_KEY = os.getenv('LABEL_STUDIO_LEGACY_API_KEY')
LABEL_STUDIO_PERSONAL_API_KEY = os.getenv('LABEL_STUDIO_PERSONAL_API_KEY')
EXPORT_DIR = '/exports/annotations'

def get_api_key():
    """Obtiene el API key, priorizando Legacy Token"""
    # Prioridad: Legacy Token > Personal Token
    if LABEL_STUDIO_LEGACY_API_KEY:
        print("Using Legacy Token (no expira, más confiable para scripts)")
        return LABEL_STUDIO_LEGACY_API_KEY, "legacy"
    elif LABEL_STUDIO_PERSONAL_API_KEY:
        print("Using Personal Access Token")
        return LABEL_STUDIO_PERSONAL_API_KEY, "personal"
    else:
        print("❌ Error: Ni LABEL_STUDIO_LEGACY_API_KEY ni LABEL_STUDIO_PERSONAL_API_KEY están definidas")
        print("\nDefine al menos una en tu archivo .env:")
        print("  LABEL_STUDIO_LEGACY_API_KEY=tu_legacy_token")
        print("  LABEL_STUDIO_PERSONAL_API_KEY=tu_personal_token")
        return None, None

api_key, token_type = get_api_key()
if not api_key:
    sys.exit(1)

try:
    client = LabelStudio(base_url=LABEL_STUDIO_URL, api_key=api_key)
    usuario = client.users.whoami()
    print(f"✅ Autenticado como: {usuario.username} ({usuario.email})\n")
except Exception as e:
    print("❌ Error de autenticación:")
    error_msg = str(e)
    
    if "401" in error_msg or "blacklist" in error_msg.lower() or "invalid" in error_msg.lower():
        print("   Token inválido o revocado")
        print("\n   Soluciones:")
        print("   1. Verifica que el token sea correcto en .env")
        if token_type == "personal":
            print("   2. Los Personal Tokens expiran, regenera uno nuevo")
        print("   3. Ve a Label Studio > Account & Settings > API Tokens")
        print("   4. Copia el token correcto a tu .env\n")
    else:
        print(f"   {e}")
        print("\n   Verifica que Label Studio esté ejecutándose\n")
    sys.exit(1)

def export_all_projects(export_format="JSON"):
    """
    Exporta todos los proyectos usando curl al API.
    Solo exporta tareas etiquetadas (download_all_tasks=false)
    """
    print(f"🚀 Iniciando exportación - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Formato: {export_format}")
    print(f"   Modo: Solo tareas etiquetadas\n")

    try:
        projects = list(client.projects.list())
        if not projects:
            print("No se encontraron proyectos para exportar.")
            return True

        print(f"📋 Encontrados {len(projects)} proyectos\n")
        os.makedirs(EXPORT_DIR, exist_ok=True)
        success_count = 0

        for project in projects:
            project_id = project.id
            project_title = project.title

            print(f"🔄 Exportando: {project_title} (ID: {project_id})")
            try:
                safe_title = "".join(
                    c for c in project_title
                    if c.isalnum() or c in (' ', '-', '_')
                ).rstrip().replace(" ", "_")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{safe_title}_{project_id}_{timestamp}.json"
                filepath = os.path.join(EXPORT_DIR, filename)

                url = f"{LABEL_STUDIO_URL.rstrip('/')}/api/projects/{project_id}/export?exportType={export_format}&download_all_tasks=false"
                
                # Usar Authorization header correcto según el tipo de token
                if token_type == "legacy":
                    auth_header = f"Authorization: Token {api_key}"
                else:  # personal
                    auth_header = f"Authorization: Bearer {api_key}"
                
                curl_cmd = [
                    "curl", "-s", "-X", "GET", url,
                    "-H", auth_header,
                    "--output", filepath,
                    "--show-error"
                ]
                
                print(f"   Descargando...")
                result = subprocess.run(curl_cmd, capture_output=True, text=True)
                
                if result.returncode == 0 and os.path.exists(filepath) and os.path.getsize(filepath) > 0:
                    file_size = os.path.getsize(filepath)
                    print(f"   ✅ Guardado: {filename}")
                    print(f"   💾 Tamaño: {file_size:,} bytes\n")
                    success_count += 1
                else:
                    print(f"   ❌ Error exportando:")
                    if result.stderr:
                        print(f"   {result.stderr}")
                    if os.path.exists(filepath) and os.path.getsize(filepath) == 0:
                        os.remove(filepath)
                    print()
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)}\n")
                
        print(f"🎉 Exportación completada: {success_count}/{len(projects)} proyectos")
        return success_count > 0

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    export_format = sys.argv[1].upper() if len(sys.argv) > 1 else "JSON"
    success = export_all_projects(export_format=export_format)
    sys.exit(0 if success else 1)