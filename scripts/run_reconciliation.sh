#!/bin/bash

# ============================================================
# run_reconciliation.sh
# Orquesta el proceso completo de conciliación bancaria.
# ============================================================

# --- Configuración ---
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/data/processed"
LOG_FILE="$LOG_DIR/reconciliation_$(date +%Y%m%d).log"
PYTHON_BIN="$PROJECT_ROOT/.venv-wsl/bin/python3"

# --- Colores para output legible en terminal ---
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color — resetea el color

# --- Función para escribir logs con timestamp ---
# Los logs son registros de lo que pasó y cuándo.
# En producción son críticos para auditoría y debugging.
log() {
    local level=$1
    local message=$2
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] [$level] $message" | tee -a "$LOG_FILE"
}

# --- Verificaciones previas ---
echo -e "${YELLOW}=================================================${NC}"
echo -e "${YELLOW}   BANK RECONCILIATION — Script de automatización${NC}"
echo -e "${YELLOW}=================================================${NC}\n"

# Verifica que el entorno virtual existe
# -f comprueba si un archivo existe
if [ ! -f "$PYTHON_BIN" ]; then
    echo -e "${RED}Error:${NC} No se encontró el entorno virtual en $PYTHON_BIN"
    echo "Ejecuta: python3 -m venv .venv-wsl && source .venv-wsl/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Verifica que hay archivos CSV para procesar
# -z comprueba si una variable está vacía
BANK_FILES=$(ls "$PROJECT_ROOT/data/bank/"*.csv 2>/dev/null)
if [ -z "$BANK_FILES" ]; then
    log "ERROR" "No hay archivos CSV en data/bank/"
    echo -e "${RED}Error:${NC} No hay archivos del banco para procesar."
    exit 1
fi

INTERNAL_FILES=$(ls "$PROJECT_ROOT/data/internal/"*.csv 2>/dev/null)
if [ -z "$INTERNAL_FILES" ]; then
    log "ERROR" "No hay archivos CSV en data/internal/"
    echo -e "${RED}Error:${NC} No hay registros internos para procesar."
    exit 1
fi

# --- Ejecución ---
log "INFO" "Iniciando proceso de conciliación"
echo -e "${GREEN}✓${NC} Verificaciones completadas, iniciando...\n"

# Ejecuta el script Python y captura el código de salida
# $? contiene el código de salida del último comando
# 0 = éxito, cualquier otro número = error
"$PYTHON_BIN" "$PROJECT_ROOT/src/main.py"
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    log "INFO" "Conciliación completada exitosamente"
    echo -e "\n${GREEN}✓ Proceso completado. Log guardado en:${NC} $LOG_FILE"
else
    log "ERROR" "El proceso falló con código $EXIT_CODE"
    echo -e "\n${RED}✗ El proceso falló.${NC} Revisa el log en: $LOG_FILE"
    exit $EXIT_CODE
fi