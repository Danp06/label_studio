#!/bin/sh

BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup
tar czf $BACKUP_DIR/label-studio-backup-$DATE.tar.gz -C / data

# Limpiar backups más antiguos de 30 días
find $BACKUP_DIR -name "label-studio-backup-*.tar.gz" -mtime +30 -delete

echo "✓ Backup completado: $BACKUP_DIR/label-studio-backup-$DATE.tar.gz" >> $BACKUP_DIR/backup.log