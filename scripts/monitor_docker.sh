#!/bin/sh

# Script de monitoreo desde contenedor Alpine
# Guarda en ./scripts/monitor_docker.sh

TIMESTAMP=$(date +"%Y-%m-%d %H:%M:%S")
DATE=$(date +"%Y%m%d")
LOG_FILE="/monitoring/metrics_${DATE}.log"

echo "========================================" >> "$LOG_FILE"
echo "MONITOREO - $TIMESTAMP" >> "$LOG_FILE"
echo "========================================" >> "$LOG_FILE"

# 1. Recursos de contenedores
echo "" >> "$LOG_FILE"
echo "--- Uso de Recursos ---" >> "$LOG_FILE"
docker stats --no-stream --format "{{.Name}}: CPU={{.CPUPerc}} MEM={{.MemUsage}} ({{.MemPerc}})" >> "$LOG_FILE" 2>/dev/null

# 2. Tiempo de respuesta
echo "" >> "$LOG_FILE"
echo "--- Tiempo de Respuesta ---" >> "$LOG_FILE"
START=$(date +%s%N)
if curl -s -f -m 10 https://labelstudio.lab.utb.edu.co/health > /dev/null 2>&1; then
    END=$(date +%s%N)
    RESPONSE_MS=$(( (END - START) / 1000000 ))
    echo "Health check: ${RESPONSE_MS}ms - OK" >> "$LOG_FILE"
else
    echo "Health check: FAILED" >> "$LOG_FILE"
fi

# 3. Conexiones de red al contenedor
echo "" >> "$LOG_FILE"
echo "--- Conexiones Activas ---" >> "$LOG_FILE"
CONNECTIONS=$(docker exec label-studio netstat -an 2>/dev/null | grep :8080 | grep ESTABLISHED | wc -l)
echo "Conexiones TCP establecidas: $CONNECTIONS" >> "$LOG_FILE"

# 4. Tamaño de volúmenes
echo "" >> "$LOG_FILE"
echo "--- Tamaño de Datos ---" >> "$LOG_FILE"
DB_SIZE=$(docker exec label-studio du -sh /label-studio/data 2>/dev/null | cut -f1 || echo "N/A")
echo "Base de datos: $DB_SIZE" >> "$LOG_FILE"

# 5. Procesos dentro del contenedor
echo "" >> "$LOG_FILE"
echo "--- Procesos Label Studio ---" >> "$LOG_FILE"
PROCS=$(docker exec label-studio ps aux 2>/dev/null | grep -c "label-studio\|gunicorn" || echo "0")
echo "Procesos activos: $PROCS" >> "$LOG_FILE"

# 6. Errores recientes
echo "" >> "$LOG_FILE"
echo "--- Errores Recientes (última hora) ---" >> "$LOG_FILE"
docker logs --since 1h label-studio 2>&1 | grep -i "error\|warning\|timeout\|failed" | tail -5 >> "$LOG_FILE" 2>/dev/null || echo "Sin errores críticos" >> "$LOG_FILE"

# 7. Resumen para alertas
echo "" >> "$LOG_FILE"
echo "--- Resumen ---" >> "$LOG_FILE"
echo "Conexiones: $CONNECTIONS | Procesos: $PROCS | DB: $DB_SIZE" >> "$LOG_FILE"

# Alertas simples
if [ "$CONNECTIONS" -gt 40 ]; then
    echo "⚠️ ALERTA: Conexiones altas ($CONNECTIONS > 40)" >> "$LOG_FILE"
fi

if [ "$RESPONSE_MS" -gt 3000 ] 2>/dev/null; then
    echo "⚠️ ALERTA: Respuesta lenta (${RESPONSE_MS}ms > 3000ms)" >> "$LOG_FILE"
fi

echo "" >> "$LOG_FILE"