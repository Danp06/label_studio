#!/bin/bash

# Script de monitoreo interno de Label Studio
# Guarda este archivo en ./scripts/monitor_performance.sh

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
DATE=$(date +"%Y%m%d")
LOG_FILE="/monitoring/performance_${DATE}.log"

# Crear directorio si no existe
mkdir -p /monitoring

echo "========================================" >> "$LOG_FILE"
echo "PERFORMANCE MONITOR - $TIMESTAMP" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. CPU y Memoria del proceso Label Studio
echo "" >> "$LOG_FILE"
echo "--- Recursos del Proceso ---" >> "$LOG_FILE"
ps aux | grep -E "label-studio|gunicorn" | grep -v grep >> "$LOG_FILE"

# 2. Memoria total del contenedor
echo "" >> "$LOG_FILE"
echo "--- Memoria del Sistema ---" >> "$LOG_FILE"
free -h >> "$LOG_FILE"

# 3. Conexiones de red
echo "" >> "$LOG_FILE"
echo "--- Conexiones de Red ---" >> "$LOG_FILE"
ESTABLISHED=$(netstat -an | grep :8080 | grep ESTABLISHED | wc -l)
TIME_WAIT=$(netstat -an | grep :8080 | grep TIME_WAIT | wc -l)
echo "Conexiones ESTABLISHED: $ESTABLISHED" >> "$LOG_FILE"
echo "Conexiones TIME_WAIT: $TIME_WAIT" >> "$LOG_FILE"

# 4. Tamaño de base de datos
echo "" >> "$LOG_FILE"
echo "--- Tamaño de Datos ---" >> "$LOG_FILE"
if [ -f /label-studio/data/label_studio.sqlite3 ]; then
    DB_SIZE=$(du -h /label-studio/data/label_studio.sqlite3 | cut -f1)
    echo "SQLite DB: $DB_SIZE" >> "$LOG_FILE"
fi
TOTAL_DATA=$(du -sh /label-studio/data | cut -f1)
echo "Total data: $TOTAL_DATA" >> "$LOG_FILE"

# 5. Disco
echo "" >> "$LOG_FILE"
echo "--- Espacio en Disco ---" >> "$LOG_FILE"
df -h /label-studio/data >> "$LOG_FILE"

# 6. Load average
echo "" >> "$LOG_FILE"
echo "--- Load Average ---" >> "$LOG_FILE"
uptime >> "$LOG_FILE"

# 7. Tiempo de respuesta interno
echo "" >> "$LOG_FILE"
echo "--- Health Check Interno ---" >> "$LOG_FILE"
START=$(date +%s%N)
if curl -s -f http://localhost:8080/health > /dev/null 2>&1; then
    END=$(date +%s%N)
    RESPONSE_MS=$(( (END - START) / 1000000 ))
    echo "Respuesta: ${RESPONSE_MS}ms" >> "$LOG_FILE"
else
    echo "Health check: FAILED" >> "$LOG_FILE"
fi

# 8. Usuarios activos (consulta a la DB)
echo "" >> "$LOG_FILE"
echo "--- Estadísticas de Usuario ---" >> "$LOG_FILE"
if command -v sqlite3 > /dev/null 2>&1 && [ -f /label-studio/data/label_studio.sqlite3 ]; then
    TOTAL_USERS=$(sqlite3 /label-studio/data/label_studio.sqlite3 "SELECT COUNT(*) FROM auth_user;" 2>/dev/null || echo "N/A")
    echo "Total usuarios: $TOTAL_USERS" >> "$LOG_FILE"
fi

# 9. Resumen CSV para análisis
CSV_FILE="/monitoring/summary_${DATE}.csv"
if [ ! -f "$CSV_FILE" ]; then
    echo "timestamp,connections,response_ms,db_size_mb,memory_used_pct" > "$CSV_FILE"
fi

# Calcular tamaño de DB en MB
if [ -f /label-studio/data/label_studio.sqlite3 ]; then
    DB_SIZE_MB=$(du -m /label-studio/data/label_studio.sqlite3 | cut -f1)
else
    DB_SIZE_MB=0
fi

# Calcular uso de memoria (%)
MEM_PCT=$(free | grep Mem | awk '{print int(($3/$2) * 100)}')

echo "$(date +%Y-%m-%d_%H:%M:%S),$ESTABLISHED,$RESPONSE_MS,$DB_SIZE_MB,$MEM_PCT" >> "$CSV_FILE"

echo "" >> "$LOG_FILE"
echo "✅ Monitoreo completado" >> "$LOG_FILE"
echo "" >> "$LOG_FILE"