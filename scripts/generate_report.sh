#!/bin/bash

# Script para generar reporte semanal
# Guarda en ./scripts/generate_report.sh

REPORT_FILE="./monitoring/REPORTE_SEMANAL_$(date +%Y%m%d).txt"

echo "========================================" > "$REPORT_FILE"
echo "   REPORTE SEMANAL - Label Studio" >> "$REPORT_FILE"
echo "   Generado: $(date +"%Y-%m-%d %H:%M:%S")" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 1. Análisis de conexiones
echo "📊 CONEXIONES CONCURRENTES" >> "$REPORT_FILE"
echo "----------------------------" >> "$REPORT_FILE"

# Buscar máximo de conexiones
MAX_CONN=$(grep "Conexiones TCP establecidas:" ./monitoring/metrics_*.log 2>/dev/null | \
    awk '{print $NF}' | sort -n | tail -1)
AVG_CONN=$(grep "Conexiones TCP establecidas:" ./monitoring/metrics_*.log 2>/dev/null | \
    awk '{sum+=$NF; count++} END {if(count>0) print int(sum/count); else print 0}')

echo "Conexiones máximas: ${MAX_CONN:-0}" >> "$REPORT_FILE"
echo "Conexiones promedio: ${AVG_CONN:-0}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 2. Análisis de tiempo de respuesta
echo "⏱️  TIEMPOS DE RESPUESTA" >> "$REPORT_FILE"
echo "----------------------------" >> "$REPORT_FILE"

MAX_RESPONSE=$(grep "Health check:" ./monitoring/metrics_*.log 2>/dev/null | \
    grep -v "FAILED" | awk '{print $3}' | sed 's/ms//' | sort -n | tail -1)
AVG_RESPONSE=$(grep "Health check:" ./monitoring/metrics_*.log 2>/dev/null | \
    grep -v "FAILED" | awk '{sum+=$3; count++} END {if(count>0) print int(sum/count); else print 0}' | sed 's/ms//')

echo "Respuesta máxima: ${MAX_RESPONSE:-0}ms" >> "$REPORT_FILE"
echo "Respuesta promedio: ${AVG_RESPONSE:-0}ms" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 3. Crecimiento de base de datos
echo "💾 CRECIMIENTO DE DATOS" >> "$REPORT_FILE"
echo "----------------------------" >> "$REPORT_FILE"

FIRST_SIZE=$(grep "Base de datos:" ./monitoring/metrics_*.log 2>/dev/null | head -1 | awk '{print $NF}')
LAST_SIZE=$(grep "Base de datos:" ./monitoring/metrics_*.log 2>/dev/null | tail -1 | awk '{print $NF}')

echo "Tamaño inicial: ${FIRST_SIZE:-N/A}" >> "$REPORT_FILE"
echo "Tamaño actual: ${LAST_SIZE:-N/A}" >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 4. Alertas detectadas
echo "⚠️  ALERTAS DETECTADAS" >> "$REPORT_FILE"
echo "----------------------------" >> "$REPORT_FILE"

ALERT_COUNT=$(grep -c "ALERTA:" ./monitoring/metrics_*.log 2>/dev/null || echo "0")
echo "Total de alertas: $ALERT_COUNT" >> "$REPORT_FILE"

if [ "$ALERT_COUNT" -gt 0 ]; then
    echo "" >> "$REPORT_FILE"
    echo "Detalle de alertas:" >> "$REPORT_FILE"
    grep "ALERTA:" ./monitoring/metrics_*.log 2>/dev/null | sort -u | head -10 >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

# 5. Resumen CSV (para gráficos)
echo "📈 DATOS PARA ANÁLISIS" >> "$REPORT_FILE"
echo "----------------------------" >> "$REPORT_FILE"
echo "Archivos CSV generados en:" >> "$REPORT_FILE"
ls -lh ./monitoring/summary_*.csv 2>/dev/null | awk '{print $9, "-", $5}' >> "$REPORT_FILE"
echo "" >> "$REPORT_FILE"

# 6. Recomendaciones
echo "💡 RECOMENDACIONES" >> "$REPORT_FILE"
echo "----------------------------" >> "$REPORT_FILE"

if [ "${MAX_CONN:-0}" -gt 50 ]; then
    echo "🔴 CRÍTICO: Más de 50 conexiones concurrentes detectadas." >> "$REPORT_FILE"
    echo "   Acción: Migrar a PostgreSQL + Redis urgente" >> "$REPORT_FILE"
elif [ "${MAX_CONN:-0}" -gt 30 ]; then
    echo "🟡 ADVERTENCIA: Entre 30-50 conexiones concurrentes." >> "$REPORT_FILE"
    echo "   Acción: Agregar Redis para caché en las próximas 2 semanas" >> "$REPORT_FILE"
else
    echo "🟢 OK: Conexiones bajo control (<30)." >> "$REPORT_FILE"
    echo "   Acción: Continuar monitoreando" >> "$REPORT_FILE"
fi
echo "" >> "$REPORT_FILE"

if [ "${MAX_RESPONSE:-0}" -gt 5000 ]; then
    echo "🔴 CRÍTICO: Tiempos de respuesta >5s detectados." >> "$REPORT_FILE"
    echo "   Acción: Optimizar inmediatamente (Redis + más recursos)" >> "$REPORT_FILE"
elif [ "${MAX_RESPONSE:-0}" -gt 3000 ]; then
    echo "🟡 ADVERTENCIA: Tiempos de respuesta entre 3-5s." >> "$REPORT_FILE"
    echo "   Acción: Planear optimizaciones para el próximo mes" >> "$REPORT_FILE"
else
    echo "🟢 OK: Tiempos de respuesta aceptables (<3s)." >> "$REPORT_FILE"
    echo "   Acción: Continuar monitoreando" >> "$REPORT_FILE"
fi

echo "" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"
echo "Reporte generado exitosamente" >> "$REPORT_FILE"
echo "========================================" >> "$REPORT_FILE"

# Mostrar en pantalla
cat "$REPORT_FILE"
echo ""
echo "📄 Reporte guardado en: $REPORT_FILE"