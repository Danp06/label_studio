# 🏷️ Sistema de Etiquetado Menu Cluvi - Label Studio

Sistema de etiquetado NER para descripciones de menú usando Label Studio con importación de CSV.

## 📋 Contenido

- [Requisitos](#requisitos)
- [Instalación](#instalación)
- [Uso](#uso)
- [Configuración del Proyecto](#configuración-del-proyecto)
- [Gestión de Backups](#gestión-de-backups)
- [Exportar Resultados](#exportar-resultados)
- [Invitar Anotadores](#invitar-anotadores)
- [Comandos Útiles](#comandos-útiles)
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

Crea un archivo `.env` en la raíz del proyecto con:

```bash
LABEL_STUDIO_PORT=8080
LABEL_STUDIO_ADMIN_USERNAME=admin@example.com
LABEL_STUDIO_ADMIN_PASSWORD=tu_contraseña_segura
```

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

## 📊 Configuración del Proyecto

### PASO 1: Crear Proyecto

1. Click en **"Create Project"**
2. Nombre: `Etiquetado Menu`
3. Click **"Save"**

### PASO 2: Importar CSV

1. Click en **"Import"** (o Settings → Import)
2. Click en **"Upload Files"**
3. Selecciona tu archivo preparado: `data/process/cluvi_preprocessed_sampled.csv` (o `data/process/cluvi_preprocessed_sampled.json`)
4. Click **"Import"**

⚠️ **Importante:** Si el CSV tiene separador `;`, Label Studio puede tener problemas. Asegúrate de usar comas (`,`).

### PASO 3: Configurar Interfaz de Etiquetado

1. Settings → **"Labeling Interface"**
2. Borra todo y pega esta configuración:

```xml
<View>
  <Style>
    .header-main { color: #4CAF50; font-weight: bold; font-size: 1.5em; margin-bottom: 10px; }
    .header-step { color: #2196F3; font-weight: bold; font-size: 1.2em; margin: 20px 0 10px; }
    .header-sub { color: #333; font-weight: bold; font-size: 1.1em; margin-top: 15px; }
    .tip { color: #666; font-style: italic; font-size: 0.9em; padding: 10px; background: #f5f5f5; border-radius: 4px; margin: 10px 0; }
    .success { color: #4CAF50; font-weight: bold; text-align: center; padding: 15px; background: #e8f5e9; border-radius: 8px; margin: 20px 0; }
    .attributes-box { background: #f9f9f9; padding: 15px; border-radius: 5px; margin: 10px 0; border-left: 4px solid #2196F3; }
  </Style>

  <!-- Main Header -->
  <Header value="¡Bienvenido/a a Anotar Menús! 🍽️" className="header-main"/>
  <Header value="Etiqueta platos, bebidas y más. Sigue los pasos, ¡es súper fácil! 😊" size="4" style="color: #666;"/>

  <!-- Step 1: Review Menu -->
  <Header value="Paso 1: Revisa el Menú" className="header-step"/>
  <View className="tip">
    <Header value="💡 Consejo: Selecciona solo las palabras exactas que representen la entidad completa (ej. 'Pizza Margherita' como PLATO, no solo 'Pizza'). Evita solapamientos y asegúrate de que cada entidad sea independiente." size="5"/>
  </View>
  <View style="display: flex; flex-direction: column; gap: 10px;">
    <Text name="text" value="Título: $label&#10;Descripción: $description&#10;Categoría: $category&#10;Categoría Principal: $main_category" granularity="word"/>
    <Labels name="entities" toName="text" smart="true" showInline="true">
      <Label value="INGREDIENTE" background="#FFB6B6"/>
      <Label value="PLATO" background="#B2DFDB"/>
      <Label value="BEBIDA" background="#BBDEFB"/>
      <Label value="MARCA" background="#FFE0B2"/>
    </Labels>
  </View>

  <!-- Step 2: Add Attributes to Entities -->
  <Header value="Paso 2: Agrega Atributos a las Entidades" className="header-step"/>

  <!-- Attributes for PLATO -->
  <View visibleWhen="region-selected" whenTagName="entities" whenLabelValue="PLATO" className="attributes-box">
    <Header value="⚙️ Atributos para PLATO:" className="header-sub"/>
    <Header value="Tipo de Plato" size="5" className="header-sub"/>
    <Choices name="course_type" toName="text" perRegion="true" choice="single" showInline="true">
      <Choice value="Entrante"/>
      <Choice value="Plato Principal"/>
      <Choice value="Acompañamiento"/>
      <Choice value="Postre"/>
    </Choices>
    <View className="tip">
      <Header value="💡 Consejo: Basado en el contexto del menú, elige el tipo que mejor encaje. Por ejemplo, usa 'Entrante' para aperitivos ligeros y 'Plato Principal' para platos fuertes." size="5"/>
    </View>
  </View>

  <!-- Attributes for BEBIDA -->
  <View visibleWhen="region-selected" whenTagName="entities" whenLabelValue="BEBIDA" className="attributes-box">
    <Header value="⚙️ Atributos para BEBIDA:" className="header-sub"/>
    <Header value="Tipo de Bebida" size="5" className="header-sub"/>
    <Choices name="beverage_type" toName="text" perRegion="true" choice="single" showInline="true">
      <Choice value="Alcohólica"/>
      <Choice value="No Alcohólica"/>
    </Choices>
    <Header value="Categoría de Bebida" size="5" className="header-sub"/>
    <Choices name="beverage_category" toName="text" perRegion="true" choice="single" showInline="true">
      <Choice value="Destilados"/>
      <Choice value="Vinos"/>
      <Choice value="Cervezas"/>
      <Choice value="Cócteles"/>
      <Choice value="Gaseosas"/>
      <Choice value="Jugos y Bebidas Naturales"/>
      <Choice value="Café o Té"/>
      <Choice value="Otro"/>
    </Choices>
    <View className="tip">
      <Header value="💡 Consejo: Usa 'Tipo de Bebida' para clasificar si es alcohólica o no (ej. 'Cerveza' → Alcohólica). Para 'Categoría', elige la más específica: 'Gaseosas' para bebidas carbonatadas comerciales (ej. 'Coca-Cola'), 'Jugos y Bebidas Naturales' para jugos frescos o smoothies (ej. 'Jugo de naranja'), 'Café o Té' para infusiones (ej. 'Capuchino'). Usa 'Otro' para casos como agua pura." size="5"/>
    </View>
  </View>

  <!-- Attributes for INGREDIENTE -->
  <View visibleWhen="region-selected" whenTagName="entities" whenLabelValue="INGREDIENTE" className="attributes-box">
    <Header value="⚙️ Atributos para INGREDIENTE:" className="header-sub"/>
    <Header value="Método de Cocción" size="5" className="header-sub"/>
    <Choices name="cooking_method" toName="text" perRegion="true" choice="multiple" showInline="true">
      <Choice value="Asado"/>
      <Choice value="Frito"/>
      <Choice value="Hervido"/>
      <Choice value="Crudo"/>
      <Choice value="Horneado"/>
      <Choice value="Al Vapor"/>
      <Choice value="Ahumado"/>
      <Choice value="Tostado"/>
      <Choice value="A la Plancha"/>
      <Choice value="Salteado"/>
      <Choice value="No Aplica"/>
    </Choices>
    <Header value="Estado de Preparación" size="5" className="header-sub"/>
    <Choices name="preparation_state" toName="text" perRegion="true" choice="single" showInline="true">
      <Choice value="Crudo"/>
      <Choice value="Cocido"/>
      <Choice value="Procesado"/>
      <Choice value="Mezclado"/>
      <Choice value="Fresco"/>
      <Choice value="Congelado"/>
      <Choice value="No Aplica"/>
    </Choices>
    <View className="tip">
      <Header value="💡 Consejo: Para ingredientes como 'tomate fresco', elige 'Fresco' en Estado y 'Crudo' en Método si no se cocina. Selecciona múltiples métodos si aplica (ej. 'Frito' y 'Ahumado'). Usa 'No Aplica' para estados únicos." size="5"/>
    </View>
  </View>

  <!-- Attributes for MARCA -->
  <View visibleWhen="region-selected" whenTagName="entities" whenLabelValue="MARCA" className="attributes-box">
    <Header value="⚙️ Atributos para MARCA:" className="header-sub"/>
    <Header value="Tipo de Marca" size="5" className="header-sub"/>
    <Choices name="brand_type" toName="text" perRegion="true" choice="single" showInline="true">
      <Choice value="Marca de Comida"/>
      <Choice value="Marca de Bebida"/>
      <Choice value="Marca de Producto"/>
    </Choices>
    <View className="tip">
      <Header value="💡 Consejo: Elige 'Marca de Comida' para marcas como 'Nestlé' en alimentos, 'Marca de Bebida' para 'Coca-Cola'. Usa 'Marca de Producto' para marcas no estándar y describe su categoría." size="5"/>
    </View>
  </View>

  <!-- Step 3: Complete Metadata -->
  <Header value="Paso 3: Completa los Metadatos" className="header-step"/>
  <Collapse accordion="true">
    <Panel value="📋 Metadatos del Menú">
      <View style="padding: 15px;">
        <Header value="Cocina de Origen" size="5" className="header-sub"/>
        <Choices name="origin_cuisine" toName="text" choice="multiple" showInline="true" required="true">
          <Choice value="Italiana"/>
          <Choice value="Peruana"/>
          <Choice value="Japonesa"/>
          <Choice value="Colombiana"/>
          <Choice value="Mexicana"/>
          <Choice value="Brasileña"/>
          <Choice value="Argentina"/>
          <Choice value="Española"/>
          <Choice value="Asiática"/>
          <Choice value="Fusión"/>
          <Choice value="Otra"/>
        </Choices>
        <View className="tip">
          <Header value="💡 Consejo: Identifica el tipo de menú revisando platos e ingredientes (ej. 'Pasta' sugiere Italiana). Selecciona múltiples si es fusión, o 'Otra' para cocinas no listadas." size="5"/>
        </View>
        <Header value="Idioma del Menú" size="5" className="header-sub"/>
        <Choices name="language" toName="text" choice="single" showInline="true" required="true">
          <Choice value="Español"/>
          <Choice value="Inglés"/>
          <Choice value="Portugués"/>
          <Choice value="Francés"/>
          <Choice value="Italiano"/>
          <Choice value="Otro"/>
        </Choices>
      </View>
    </Panel>
  </Collapse>

  <!-- Final Message -->
  <View className="success">
    <Header value="✨ ¡Último paso! Revisa que todas las entidades tengan atributos correctos y consistentes. ¡Lo hiciste genial! ✨" size="4"/>
  </View>
</View>
```

3. Click **"Save"**

---

## 💾 Gestión de Backups

### Backups Automáticos

Los backups se ejecutan automáticamente **3 veces al día** (6 AM, 2 PM, 10 PM) y se guardan en la carpeta `./backups/`.

### Ejecutar Backup Manual

```bash
./scripts/backup.sh
```

Este comando realiza un backup inmediato sin detener los servicios.

### Restaurar desde Backup

```bash
./scripts/restore.sh
```

Este script te permite:
1. Ver todos los backups disponibles
2. Elegir el más reciente o seleccionar uno específico
3. Restaurar los datos (con confirmación de seguridad)
4. Reiniciar automáticamente los servicios

**Flujo:**
- Detiene los contenedores
- Elimina el volumen actual
- Restaura los datos del backup
- Reinicia los servicios

⚠️ **Advertencia:** La restauración elimina todos los datos actuales. Asegúrate de seleccionar el backup correcto.

### Ubicación de Backups

```
./backups/
├── label-studio-backup-20240115_060000.tar.gz
├── label-studio-backup-20240115_140000.tar.gz
├── label-studio-backup-20240115_220000.tar.gz
└── backup.log
```

Los backups se conservan durante 30 días y se limpian automáticamente después.

---

## 📤 Exportar Resultados

### Desde la UI

1. En el proyecto, click en **"Export"**
2. Selecciona formato: **JSON** o **CSV**
3. Click **"Export"**

### Formato de Exportación

Los resultados incluirán:
- Entidades etiquetadas (INGREDIENTE, PLATO, BEBIDA, MARCA)
- Atributos de cada entidad
- Metadatos del menú (cocina de origen, idioma)

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
├── docker-compose.yml              # Configuración Docker
├── .env                            # Variables de entorno (crear)
├── scripts/
│   ├── backup.sh                   # Script de backup manual
│   └── restore.sh                  # Script de restauración
├── backups/                        # Backups automáticos (creado automáticamente)
├── data/
│   ├── raw/                        # Datos fuente (entrada)
│   │   ├── cluvi_preprocessed.csv
│   │   ├── cluvi_preprocessed.json
│   │   └── cluvi_preprocessed.parquet
│   └── process/                    # Datos preparados para Label Studio
│       ├── cluvi_preprocessed_sampled.csv
│       ├── cluvi_preprocessed_sampled.json
│       └── cluvi_preprocessed_sampled.parquet
├── exports/                        # Resultados exportados por Label Studio
└── README.md                       # Esta guía
```

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

### Label Studio no inicia

```bash
docker-compose logs -f labelstudio
```

Revisa si hay errores en los logs. Problema común: puerto 8080 en uso.

### Página en blanco

- Limpia la caché del navegador (Ctrl+Shift+Del)
- Accede directamente a: `http://localhost:8080/user/login/`
- Reinicia el contenedor: `docker-compose restart`

### Advertencia de contenedores huérfanos

```
WARNING: Found orphan containers (label-studio-db)
```

Ejecuta:
```bash
docker-compose down --remove-orphans
docker-compose up -d
```

Esto sucede cuando eliminas servicios del `docker-compose.yml` pero sus contenedores siguen existiendo.

### Problemas con permisos en backups

Si ves errores de permisos al restaurar, asegúrate de que los scripts sean ejecutables:

```bash
chmod +x scripts/backup.sh
chmod +x scripts/restore.sh
```

---

## 📚 Recursos

- [Documentación Label Studio](https://labelstud.io/guide/)
- [Label Studio API](https://labelstud.io/api/)
- [Guía de Etiquetado NER](https://labelstud.io/templates/named_entity.html)
- [Docker Compose Documentation](https://docs.docker.com/compose/)

---

## 📞 Soporte

Para problemas o dudas:
1. Revisa los logs: `docker-compose logs -f`
2. Consulta la documentación oficial
3. Verifica que todos los archivos estén en su lugar
4. Asegúrate de que los permisos de los scripts sean correctos