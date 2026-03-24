#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
RECONCILIATION_SCRIPT="$SCRIPT_DIR/run_reconciliation.sh"

CRON_JOB="0 2 * * * $RECONCILIATION_SCRIPT >> $PROJECT_ROOT/data/processed/cron.log 2>&1"

echo "Configurando cron job..."
echo "Tarea: $CRON_JOB"

(crontab -l 2>/dev/null | grep -v "$RECONCILIATION_SCRIPT"; echo "$CRON_JOB") | crontab -

echo "✓ Cron job configurado. Se ejecutará diariamente a las 2:00am."
echo ""
echo "Para verificar que quedó registrado ejecuta:"
echo "  crontab -l"