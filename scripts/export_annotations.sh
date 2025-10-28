#!/bin/bash

# Wrapper para exportación desde el contenedor labelstudio
# Se ejecuta via cron dentro del mismo contenedor labelstudio

set -e

LOG_DIR="/exports/logs"
LOG_FILE="$LOG_DIR/export_$(date +%Y%m%d_%H%M%S).log"

# Crear directorio de logs
mkdir -p "$LOG_DIR"

echo "=== Exportación desde Label Studio ===" > "$LOG_FILE"
echo "Fecha: $(date)" >> "$LOG_FILE"
echo "======================================" >> "$LOG_FILE"

# Usar la ruta completa del virtualenv de Label Studio
if /label-studio/.venv/bin/python3 /scripts/export_annotations.py >> "$LOG_FILE" 2>&1; then
    echo "✅ Exportación completada exitosamente" >> "$LOG_FILE"
else
    echo "❌ Exportación falló" >> "$LOG_FILE"
fi

echo "======================================" >> "$LOG_FILE"
echo "Fin: $(date)" >> "$LOG_FILE"

# Rotar logs (mantener últimos 10)
ls -t "$LOG_DIR"/export_*.log 2>/dev/null | tail -n +11 | xargs rm -f -- 2>/dev/null || true