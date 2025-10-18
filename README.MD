# 🏷️ Sistema de Etiquetado Menu Cluvi - Label Studio

Sistema completo de etiquetado NER para descripciones de menú usando Label Studio con automatización de proyectos, gestión de backups y exportación de datos.

## 📋 Contenido

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Configuración de Variables de Entorno](#configuración-de-variables-de-entorno)
- [Uso](#uso)
- [Gestión Automática de Proyectos](#gestión-automática-de-proyectos)
- [Scripts de Automatización](#scripts-de-automatización)
- [Gestión de Backups](#gestión-de-backups)
- [Exportar Resultados](#exportar-resultados)
- [API y Autenticación](#api-y-autenticación)
- [Invitar Anotadores](#invitar-anotadores)
- [Comandos Útiles](#comandos-útiles)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Solución de Problemas](#solución-de-problemas)

---

## 🛠️ Requisitos

- Docker
- Docker Compose
- Python 3.8+
- pip (para instalar dependencias Python)
- (Opcional) virtualenv/venv para aislar dependencias

---

## 🚀 Instalación

### 1. Clonar y preparar el proyecto

```bash
# Estructura de carpetas
mkdir -p data/raw data/process exports scripts backups
```

### 1.b (Opcional) Crear y activar entorno virtual

```bash
# Crear entorno virtual (recomendado)
python3 -m venv .venv

# Activar el entorno virtual
source .venv/bin/activate

# Alternativa: usar el ayudante para detectar/activar entornos
source ./activate_env.sh
```

### 1.c Instalar dependencias Python

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

Nota: estas dependencias se usan principalmente para los scripts de preparación de datos y utilidades locales. Label Studio corre con Docker.

### 2. Preparar el CSV (OPCIONAL)

Si tu CSV tiene muchos registros, debes limitarlos.

### 2.b Configurar variables de entorno (.env)

Crea un archivo `.env` en la raíz del proyecto con las siguientes variables:

```bash
# Configuración básica de Label Studio
LABEL_STUDIO_PORT=8080
LABEL_STUDIO_ADMIN_USERNAME=admin@example.com
LABEL_STUDIO_ADMIN_PASSWORD=tu_contraseña_segura

# URLs y configuración de API
LABEL_STUDIO_URL=http://localhost:8080

# API Keys (obtén estos desde Label Studio > Account & Settings > API Tokens)
LABEL_STUDIO_LEGACY_API_KEY=tu_legacy_token_aqui
LABEL_STUDIO_PERSONAL_API_KEY=tu_personal_token_aqui

# Configuración de zona horaria
TZ=America/Bogota
```

**⚠️ Importante:** 
- El archivo `.env` está en `.gitignore` por seguridad
- Los API tokens son necesarios para la automatización de scripts
- Usa `LABEL_STUDIO_LEGACY_API_KEY` para scripts automatizados (no expira)
- Usa `LABEL_STUDIO_PERSONAL_API_KEY` como alternativa (puede expirar)

### 3. Iniciar Label Studio

```bash
docker-compose up -d
```

### 4. Acceder a Label Studio

```
http://localhost:8080
```

**Credenciales:**
- Email: (la que configuraste en `.env`)
- Password: (la que configuraste en `.env`)

---

## ⚙️ Configuración de Variables de Entorno

### Obtener API Tokens

1. **Accede a Label Studio:** `http://localhost:8080`
2. **Ve a:** Account & Settings → API Tokens
3. **Crea dos tokens:**
   - **Legacy Token:** Para scripts automatizados (no expira)
   - **Personal Access Token:** Como alternativa (puede expirar)

### Variables Requeridas

| Variable | Descripción | Ejemplo |
|----------|-------------|---------|
| `LABEL_STUDIO_PORT` | Puerto de acceso | `8080` |
| `LABEL_STUDIO_ADMIN_USERNAME` | Usuario administrador | `admin@example.com` |
| `LABEL_STUDIO_ADMIN_PASSWORD` | Contraseña administrador | `mi_password_seguro` |
| `LABEL_STUDIO_URL` | URL base de la API | `http://localhost:8080` |
| `LABEL_STUDIO_LEGACY_API_KEY` | Token para scripts | `abc123...` |
| `LABEL_STUDIO_PERSONAL_API_KEY` | Token personal | `xyz789...` |

---

## 📊 Configuración del Proyecto

### Método Automático (Recomendado)

El sistema crea automáticamente proyectos al iniciar. Los proyectos se definen en `projects/projects_index.json`:

```json
{
    "Etiquetado Menu test": {
        "schema": "menu_schema.xml",
        "data_source": "process/cluvi_preprocessed_sampled.json"
    }
}
```

**Estructura del archivo:**
- `schema`: Archivo XML con la configuración de etiquetado
- `data_source`: Archivo JSON con los datos a etiquetar

### Método Manual

Si prefieres crear proyectos manualmente:

#### PASO 1: Crear Proyecto

1. Click en **"Create Project"**
2. Nombre: `Etiquetado Menu`
3. Click **"Save"**

#### PASO 2: Importar CSV

1. Click en **"Import"** (o Settings → Import)
2. Click en **"Upload Files"**
3. Selecciona tu archivo preparado: `data/process/cluvi_preprocessed_sampled.csv` (o `data/process/cluvi_preprocessed_sampled.json`)
4. Click **"Import"**

⚠️ **Importante:** Si el CSV tiene separador `;`, Label Studio puede tener problemas. Asegúrate de usar comas (`,`).

#### PASO 3: Configurar Interfaz de Etiquetado

1. Settings → **"Labeling Interface"**
2. Borra todo y pega la configuración desde `projects/menu_schema.xml`
3. Click **"Save"**

---

## 🤖 Gestión Automática de Proyectos

### Configuración de Proyectos

Los proyectos se gestionan automáticamente mediante el archivo `projects/projects_index.json`:

```json
{
    "Nombre del Proyecto": {
        "schema": "menu_schema.xml",
        "data_source": "process/cluvi_preprocessed_sampled.json"
    }
}
```

### Archivos de Configuración

- **`projects/menu_schema.xml`**: Configuración completa de la interfaz de etiquetado
- **`projects/projects_index.json`**: Índice de proyectos con sus configuraciones
- **`data/process/`**: Archivos de datos preparados para importar

### Crear Nuevo Proyecto

1. **Agrega el proyecto** a `projects/projects_index.json`
2. **Prepara los datos** en formato JSON en `data/process/`
3. **Reinicia el sistema**: `docker-compose restart`
4. **El proyecto se crea automáticamente** con datos importados

### Scripts de Gestión

- **`create_project.py`**: Crea proyectos automáticamente al iniciar
- **`add_task_to_project.py`**: Agrega nuevas tareas a proyectos existentes
- **`delete_project.py`**: Elimina proyectos específicos
- **`delete_task_to_project.py`**: Elimina tareas específicas de proyectos

---

## 🔧 Scripts de Automatización

### Scripts Principales

| Script | Función | Uso |
|--------|---------|-----|
| `create_project.py` | Crear proyectos automáticamente | Ejecuta al iniciar Label Studio |
| `add_task_to_project.py` | Agregar tareas a proyectos | `python3 scripts/add_task_to_project.py` |
| `delete_project.py` | Eliminar proyectos | `python3 scripts/delete_project.py` |
| `delete_task_to_project.py` | Eliminar tareas específicas | `python3 scripts/delete_task_to_project.py` |
| `export_annotations.py` | Exportar anotaciones | `python3 scripts/export_annotations.py` |

### Scripts de Sistema

| Script | Función | Uso |
|--------|---------|-----|
| `backup.sh` | Backup automático | Ejecuta 3 veces al día |
| `restore.sh` | Restaurar desde backup | `./scripts/restore.sh` |
| `export_annotations.sh` | Exportar anotaciones (shell) | Ejecuta automáticamente |

### Ejecutar Scripts Manualmente

```bash
# Activar entorno virtual
source activate_env.sh

# Crear proyecto manualmente
python3 scripts/create_project.py

# Agregar tareas a proyecto existente
python3 scripts/add_task_to_project.py

# Exportar anotaciones
python3 scripts/export_annotations.py JSON
```

---

## 💾 Gestión de Backups

### Backups Automáticos

Los backups se ejecutan automáticamente **3 veces al día** (6 AM, 2 PM, 10 PM) y se guardan en la carpeta `./backups/`.

**Características:**
- ✅ Backups automáticos cada 8 horas
- ✅ Limpieza automática de backups antiguos (>30 días)
- ✅ Logs de backup en `backups/backup.log`
- ✅ Compresión con tar.gz para optimizar espacio

### Ejecutar Backup Manual

```bash
# Backup inmediato desde contenedor
docker exec label-studio-backup /backup.sh

# Backup manual desde host
./scripts/backup.sh
```

### Restaurar desde Backup

```bash
# Usar el script interactivo (recomendado)
./scripts/restore.sh
```

**El script de restauración te permite:**
1. **Ver todos los backups disponibles** con fechas y tamaños
2. **Elegir el más reciente** o seleccionar uno específico
3. **Confirmar la operación** antes de proceder
4. **Restaurar automáticamente** con reinicio de servicios

**Flujo de restauración:**
- 🛑 Detiene los contenedores
- 🗑️ Elimina el volumen actual
- 📦 Restaura los datos del backup
- 🚀 Reinicia los servicios automáticamente

⚠️ **Advertencia:** La restauración elimina todos los datos actuales. Asegúrate de seleccionar el backup correcto.

### Ubicación de Backups

```
./backups/
├── label-studio-backup-20240115_060000.tar.gz
├── label-studio-backup-20240115_140000.tar.gz
├── label-studio-backup-20240115_220000.tar.gz
└── backup.log
```

**Política de retención:**
- Backups se conservan durante **30 días**
- Limpieza automática de archivos antiguos
- Logs de backup se mantienen indefinidamente

---

## 📤 Exportar Resultados

### Exportación Automática

El sistema exporta automáticamente las anotaciones **3 veces al día** (6 AM, 2 PM, 10 PM) a la carpeta `./exports/annotations/`.

### Exportación Manual

#### Desde la UI
1. En el proyecto, click en **"Export"**
2. Selecciona formato: **JSON** o **CSV**
3. Click **"Export"**

#### Desde Scripts

```bash
# Activar entorno virtual
source activate_env.sh

# Exportar todos los proyectos
python3 scripts/export_annotations.py JSON

# Exportar con formato específico
python3 scripts/export_annotations.py CSV
```

### Formato de Exportación

Los resultados incluirán:
- **Entidades etiquetadas:** INGREDIENTE, PLATO, BEBIDA, MARCA
- **Atributos de cada entidad:** Métodos de cocción, tipos, categorías
- **Metadatos del menú:** Cocina de origen, idioma
- **Metadatos técnicos:** Timestamp, ID de proyecto, usuario anotador

### Ubicación de Exports

```
./exports/
├── annotations/
│   ├── Etiquetado_Menu_test_1_20240115_140000.json
│   ├── Etiquetado_Menu_test_1_20240115_220000.json
│   └── logs/
└── logs/
```

---

## 🔑 API y Autenticación

### Tipos de Tokens

| Tipo | Descripción | Duración | Uso Recomendado |
|------|-------------|----------|-----------------|
| **Legacy Token** | Token tradicional | No expira | Scripts automatizados |
| **Personal Access Token** | Token personal | Configurable | Desarrollo y pruebas |

### Obtener Tokens

1. **Accede a Label Studio:** `http://localhost:8080`
2. **Ve a:** Account & Settings → API Tokens
3. **Crea Legacy Token:**
   - Click "Create Legacy Token"
   - Copia el token generado
   - Agrégalo a `.env` como `LABEL_STUDIO_LEGACY_API_KEY`
4. **Crea Personal Token (opcional):**
   - Click "Create Personal Access Token"
   - Configura expiración
   - Agrégalo a `.env` como `LABEL_STUDIO_PERSONAL_API_KEY`

### Configuración en .env

```bash
# Prioridad: Legacy Token > Personal Token
LABEL_STUDIO_LEGACY_API_KEY=abc123def456...
LABEL_STUDIO_PERSONAL_API_KEY=xyz789uvw012...
LABEL_STUDIO_URL=http://localhost:8080
```

### Verificar Autenticación

```bash
# Activar entorno virtual
source activate_env.sh

# Probar conexión
python -c "
from label_studio_sdk import LabelStudio
from dotenv import load_dotenv
import os
load_dotenv()
client = LabelStudio(base_url=os.getenv('LABEL_STUDIO_URL'), api_key=os.getenv('LABEL_STUDIO_LEGACY_API_KEY'))
print('✅ Conectado como:', client.users.whoami().username)
"
```

### Solución de Problemas de API

**Error 401 - Token inválido:**
- Verifica que el token sea correcto en `.env`
- Regenera el token si es Personal Access Token
- Usa Legacy Token para mayor estabilidad

**Error de conexión:**
- Verifica que Label Studio esté ejecutándose
- Confirma la URL en `LABEL_STUDIO_URL`
- Revisa los logs: `docker-compose logs -f labelstudio`

---

## 👥 Invitar Anotadores

1. Click en **"Organization"** → **"Members"**
2. Click **"Add Member"**
3. Email del anotador
4. Rol: **"Annotator"** (solo etiquetan, NO configuran)
5. Click **"Send Invitation"**

**Notas:**
- Solo Admins pueden crear proyectos y eliminar datos
- Los Annotators solo pueden etiquetar
- La invitación se envía por correo

---

## 🔧 Comandos Útiles

```bash
# Ver logs de Label Studio
docker-compose logs -f labelstudio

# Ver logs del servicio de backup
docker-compose logs -f backup

# Ver estado de todos los servicios
docker-compose ps

# Reiniciar Label Studio
docker-compose restart labelstudio

# Detener todo sin eliminar datos
docker-compose down

# Detener y eliminar datos (⚠️ cuidado)
docker-compose down -v

# Limpiar contenedores huérfanos
docker-compose down --remove-orphans
```

---

## 📁 Estructura del Proyecto

```
.
├── docker-compose.yml              # Configuración Docker con servicios
├── .env                           # Variables de entorno (crear)
├── .gitignore                     # Archivos ignorados por Git
├── requirements.txt               # Dependencias Python
├── activate_env.sh                 # Script para activar entorno virtual
├── README.MD                      # Esta guía completa
│
├── scripts/                       # Scripts de automatización
│   ├── create_project.py          # Crear proyectos automáticamente
│   ├── add_task_to_project.py     # Agregar tareas a proyectos
│   ├── delete_project.py          # Eliminar proyectos
│   ├── delete_task_to_project.py  # Eliminar tareas específicas
│   ├── export_annotations.py      # Exportar anotaciones (Python)
│   ├── export_annotations.sh      # Exportar anotaciones (Shell)
│   ├── backup.sh                  # Script de backup manual
│   └── restore.sh                 # Script de restauración interactivo
│
├── projects/                      # Configuración de proyectos
│   ├── menu_schema.xml            # Schema de etiquetado NER
│   └── projects_index.json        # Índice de proyectos y datos
│
├── data/                          # Datos del proyecto
│   ├── raw/                       # Datos fuente originales
│   │   ├── cluvi_preprocessed.csv
│   │   ├── cluvi_preprocessed.json
│   │   └── cluvi_preprocessed.parquet
│   └── process/                   # Datos preparados para Label Studio
│       ├── cluvi_preprocessed_sampled.csv
│       ├── cluvi_preprocessed_sampled.json
│       └── cluvi_preprocessed_sampled.parquet
│
├── exports/                       # Resultados exportados
│   ├── annotations/               # Anotaciones exportadas automáticamente
│   └── logs/                      # Logs de exportación
│
├── backups/                       # Backups automáticos (creado automáticamente)
│   ├── label-studio-backup-*.tar.gz
│   └── backup.log
│
└── .venv/                         # Entorno virtual Python (opcional)
```

### Archivos Clave

| Archivo | Propósito |
|---------|-----------|
| `docker-compose.yml` | Configuración completa de servicios Docker |
| `.env` | Variables de entorno y configuración |
| `projects/menu_schema.xml` | Interfaz de etiquetado NER completa |
| `projects/projects_index.json` | Configuración de proyectos automáticos |
| `scripts/create_project.py` | Automatización de creación de proyectos |
| `activate_env.sh` | Gestión inteligente de entornos virtuales |

---

## ⚠️ Notas Importantes

### Separador de CSV

Label Studio espera CSVs con **coma (`,`)** como separador. Si tu archivo usa punto y coma (`;`), conviértelo primero.

### Columnas para etiquetar

Asegúrate de que tu CSV tenga las siguientes columnas:
- `label`: Título del plato
- `description`: Descripción del plato
- `category`: Categoría del plato
- `main_category`: Categoría principal

El sistema combinará automáticamente estas columnas en un solo texto para etiquetar. Si tus columnas tienen otros nombres, ajusta las referencias `$label`, `$description`, `$category`, y `$main_category` en la configuración XML.

---

## 🚨 Solución de Problemas

### Problemas de Inicio

#### Label Studio no inicia

```bash
# Ver logs detallados
docker-compose logs -f labelstudio

# Verificar puerto en uso
netstat -tulpn | grep :8080
```

**Soluciones comunes:**
- Puerto 8080 ocupado: Cambia `LABEL_STUDIO_PORT` en `.env`
- Permisos incorrectos: `chmod +x scripts/*.sh`
- Variables de entorno faltantes: Verifica `.env`

#### Página en blanco o errores de carga

```bash
# Limpiar caché del navegador
Ctrl+Shift+Del

# Acceso directo
http://localhost:8080/user/login/

# Reiniciar contenedores
docker-compose restart
```

### Problemas de API y Autenticación

#### Error 401 - Token inválido

```bash
# Verificar tokens en .env
cat .env | grep API_KEY

# Probar conexión
python -c "
from label_studio_sdk import LabelStudio
from dotenv import load_dotenv
import os
load_dotenv()
try:
    client = LabelStudio(base_url=os.getenv('LABEL_STUDIO_URL'), api_key=os.getenv('LABEL_STUDIO_LEGACY_API_KEY'))
    print('✅ Token válido:', client.users.whoami().username)
except Exception as e:
    print('❌ Error:', e)
"
```

**Soluciones:**
- Regenera el token en Label Studio > Account & Settings > API Tokens
- Usa Legacy Token en lugar de Personal Token
- Verifica que el token esté completo en `.env`

#### Error de conexión a API

```bash
# Verificar que Label Studio esté ejecutándose
docker-compose ps

# Verificar URL
echo $LABEL_STUDIO_URL

# Probar conectividad
curl -I http://localhost:8080/api/health/
```

### Problemas de Docker

#### Contenedores huérfanos

```
WARNING: Found orphan containers (label-studio-db)
```

```bash
# Limpiar contenedores huérfanos
docker-compose down --remove-orphans
docker-compose up -d
```

#### Problemas de volúmenes

```bash
# Ver volúmenes existentes
docker volume ls

# Eliminar volumen corrupto
docker volume rm label_studio_data
docker volume create label_studio_data

# Reiniciar servicios
docker-compose up -d
```

### Problemas de Scripts

#### Permisos de ejecución

```bash
# Hacer scripts ejecutables
chmod +x scripts/*.sh
chmod +x scripts/*.py
```

#### Entorno virtual no activado

```bash
# Usar script de activación automática
source activate_env.sh

# Verificar entorno activo
which python
which pip
```

#### Dependencias faltantes

```bash
# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
pip list | grep label-studio
```

### Problemas de Backups

#### Backup fallido

```bash
# Ver logs de backup
cat backups/backup.log

# Ejecutar backup manual
docker exec label-studio-backup /backup.sh

# Verificar espacio en disco
df -h
```

#### Restauración fallida

```bash
# Verificar integridad del backup
tar -tzf backups/label-studio-backup-*.tar.gz

# Restaurar con script interactivo
./scripts/restore.sh
```

### Problemas de Datos

#### Proyecto no se crea automáticamente

```bash
# Verificar configuración
cat projects/projects_index.json

# Verificar datos
ls -la data/process/

# Ejecutar creación manual
python3 scripts/create_project.py
```

#### Datos no se importan

```bash
# Verificar formato JSON
python -c "
import json
with open('data/process/cluvi_preprocessed_sampled.json') as f:
    data = json.load(f)
    print('✅ JSON válido, registros:', len(data))
"
```

### Logs y Diagnóstico

#### Ver todos los logs

```bash
# Logs de todos los servicios
docker-compose logs -f

# Logs específicos
docker-compose logs -f labelstudio
docker-compose logs -f backup
```

#### Estado del sistema

```bash
# Estado de contenedores
docker-compose ps

# Uso de recursos
docker stats

# Espacio en disco
df -h
du -sh backups/ exports/
```

---

## 📚 Recursos

### Documentación Oficial

- [Label Studio Documentation](https://labelstud.io/guide/)
- [Label Studio API Reference](https://labelstud.io/api/)
- [Label Studio SDK Documentation](https://labelstud.io/sdk/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

### Guías Específicas

- [Named Entity Recognition (NER) Template](https://labelstud.io/templates/named_entity.html)
- [Label Studio Configuration Guide](https://labelstud.io/guide/setup.html)
- [API Authentication Guide](https://labelstud.io/guide/api.html)

### Herramientas Relacionadas

- [Label Studio Community](https://github.com/heartexlabs/label-studio)
- [Label Studio Templates](https://labelstud.io/templates/)
- [Label Studio Integrations](https://labelstud.io/integrations/)

---

## 📞 Soporte

### Antes de Contactar

1. **Revisa los logs:** `docker-compose logs -f`
2. **Consulta esta documentación** completa
3. **Verifica la configuración** en `.env`
4. **Ejecuta diagnósticos:** `docker-compose ps` y `df -h`

### Problemas Comunes

- **Token API inválido:** Regenera en Label Studio > Account & Settings > API Tokens
- **Puerto ocupado:** Cambia `LABEL_STUDIO_PORT` en `.env`
- **Proyecto no se crea:** Verifica `projects/projects_index.json` y datos en `data/process/`
- **Backup fallido:** Verifica espacio en disco y permisos

### Información del Sistema

```bash
# Información completa del sistema
echo "=== Docker Compose Status ==="
docker-compose ps

echo "=== Disk Usage ==="
df -h

echo "=== Backup Status ==="
ls -la backups/

echo "=== Export Status ==="
ls -la exports/

echo "=== Environment Check ==="
cat .env | grep -E "(PORT|URL|API_KEY)" | head -5
```

---

## 🎯 Resumen de Características

### ✅ Funcionalidades Implementadas

- **🤖 Automatización completa** de creación de proyectos
- **💾 Backups automáticos** cada 8 horas con retención de 30 días
- **📤 Exportación automática** de anotaciones
- **🔑 Gestión de API tokens** con autenticación robusta
- **📊 Interfaz de etiquetado NER** completa y personalizada
- **🔧 Scripts de gestión** para todas las operaciones
- **🐳 Configuración Docker** optimizada con servicios separados
- **📁 Estructura organizada** con separación clara de responsabilidades

### 🚀 Próximas Mejoras Sugeridas

- **🔄 Sincronización automática** con repositorios Git
---

*Última actualización: $(date +%Y-%m-%d)*