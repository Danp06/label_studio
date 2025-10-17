#!/bin/bash

BACKUP_DIR="./backups"

echo "╔════════════════════════════════════════╗"
echo "║  Restaurar Backup - Label Studio      ║"
echo "╚════════════════════════════════════════╝"
echo ""

# Function to list backups
list_backups() {
  echo "📦 Backups disponibles:"
  BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/label-studio-backup-*.tar.gz 2>/dev/null | wc -l)

  if [ "$BACKUP_COUNT" -eq 0 ]; then
    echo "❌ No hay backups disponibles en $BACKUP_DIR"
    return 1 # Indicate no backups
  else
    echo ""
    ls -lh "$BACKUP_DIR"/label-studio-backup-*.tar.gz 2>/dev/null | awk '{print $9, "(" $5 ")"}' | nl
    echo ""
    return 0 # Indicate backups found
  fi
}

# Initial listing of backups
if ! list_backups; then
  exit 1 # Exit if no backups found initially
fi

BACKUP_FILE="" # Initialize BACKUP_FILE

while true; do
  echo "¿Qué acción deseas realizar?"
  echo "1) Restaurar el backup más reciente (recomendado)"
  echo "2) Restaurar un backup específico"
  echo "3) Listar backups disponibles"
  echo "4) Salir"
  echo ""
  read -p "Opción (1, 2, 3 o 4): " option

  case "$option" in
    1)
      BACKUP_FILE=$(ls -t "$BACKUP_DIR"/label-studio-backup-*.tar.gz | head -1)
      echo ""
      echo "✓ Restaurando: $(basename "$BACKUP_FILE")"
      break # Exit loop to proceed with restoration
      ;;
    2)
      echo ""
      read -p "Nombre del backup (ej: label-studio-backup-20240115_140000.tar.gz): " backup_name
      BACKUP_FILE="$BACKUP_DIR/$backup_name"
      
      if [ ! -f "$BACKUP_FILE" ]; then
        echo "❌ Backup no encontrado: $BACKUP_FILE"
        continue # Stay in loop to choose again
      fi
      break # Exit loop to proceed with restoration
      ;;
    3)
      echo ""
      list_backups
      ;;
    4)
      echo "❌ Operación cancelada. Saliendo."
      exit 0
      ;;
    *)
      echo "❌ Opción inválida. Por favor, elige 1, 2, 3 o 4."
      ;;
  esac
  echo ""
done

echo ""
echo "⚠️  ADVERTENCIA: Esto eliminará todos los datos actuales"
echo "📁 Backup a restaurar: $(basename "$BACKUP_FILE")"
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
  -v "$(pwd)"/backups:/backups \
  alpine tar xzf /backups/"$(basename "$BACKUP_FILE")" -C /

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