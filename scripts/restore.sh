#!/bin/bash

BACKUP_DIR="./backups"

echo "╔════════════════════════════════════════╗"
echo "║  Restaurar Backup - Label Studio      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Listar backups disponibles
echo "📦 Backups disponibles:"
echo ""
ls -lh $BACKUP_DIR/label-studio-backup-*.tar.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}' | nl

if [ $(ls -1 $BACKUP_DIR/label-studio-backup-*.tar.gz 2>/dev/null | wc -l) -eq 0 ]; then
  echo "❌ No hay backups disponibles en $BACKUP_DIR"
  exit 1
fi

echo ""
echo "¿Cuál backup quieres restaurar?"
echo "1) El más reciente (recomendado)"
echo "2) Seleccionar uno específico"
echo ""
read -p "Opción (1 o 2): " option

if [ "$option" == "1" ]; then
  BACKUP_FILE=$(ls -t $BACKUP_DIR/label-studio-backup-*.tar.gz | head -1)
  echo ""
  echo "✓ Restaurando: $(basename $BACKUP_FILE)"
elif [ "$option" == "2" ]; then
  echo ""
  read -p "Nombre del backup (ej: label-studio-backup-20240115_140000.tar.gz): " backup_name
  BACKUP_FILE="$BACKUP_DIR/$backup_name"
  
  if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Backup no encontrado: $BACKUP_FILE"
    exit 1
  fi
else
  echo "❌ Opción inválida"
  exit 1
fi

echo ""
echo "⚠️  ADVERTENCIA: Esto eliminará todos los datos actuales"
echo "📁 Backup a restaurar: $(basename $BACKUP_FILE)"
echo ""
read -p "¿Estás seguro? (escribe 'si' para continuar): " confirm

if [ "$confirm" != "si" ]; then
  echo "❌ Operación cancelada"
  exit 1
fi

echo ""
echo "🛑 Deteniendo contenedores..."
docker-compose down

echo "🗑️  Eliminando volumen actual..."
docker volume rm label_studio_data

echo "📦 Creando volumen nuevo..."
docker volume create label_studio_data

echo "📥 Restaurando backup..."
docker run --rm \
  -v label_studio_data:/data \
  -v $(pwd)/backups:/backups \
  alpine tar xzf /backups/$(basename $BACKUP_FILE) -C /

if [ $? -eq 0 ]; then
  echo "✅ Backup restaurado exitosamente"
else
  echo "❌ Error al restaurar el backup"
  exit 1
fi

echo "🚀 Iniciando contenedores..."
docker-compose up -d

echo ""
echo "✨ ¡Restauración completada!"
echo "📍 Label Studio estará disponible en unos momentos..."
echo ""
docker logs label-studio -f --tail 20