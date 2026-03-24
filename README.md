# Bank Reconciliation 🏦

Automatización del proceso de conciliación bancaria usando Python, SQL y Bash.
Detecta discrepancias entre reportes bancarios y registros internos sin intervención manual.

## ¿Qué problema resuelve?

En empresas financieras, comparar el estado de cuenta del banco contra los registros
internos se hace manualmente en Excel y puede tomar horas. Este sistema lo automatiza
completamente y genera un reporte de discrepancias en segundos.

## ¿Qué detecta?

- Transacciones que existen en el banco pero no en registros internos
- Transacciones registradas internamente sin contraparte bancaria
- Transacciones con montos diferentes entre ambas fuentes

## Stack técnico

- **Python 3.12** — lenguaje principal
- **Pandas** — carga, limpieza y comparación de datos con merge/join
- **SQLite** — almacenamiento de resultados
- **Rich** — visualización de tablas y paneles en terminal
- **Bash** — automatización y orquestación del proceso
- **Cron** — programación de tareas automáticas (configuración incluida)

## Estructura
```
bank-reconciliation/
├── data/
│   ├── bank/           # Reportes del banco (CSV)
│   ├── internal/       # Registros internos (CSV)
│   └── processed/      # Reportes generados y logs
├── scripts/
│   ├── run_reconciliation.sh   # Orquesta el proceso completo
│   └── setup_cron.sh           # Configura tarea programada diaria
├── src/
│   ├── loader.py       # Carga y validación de CSVs
│   ├── reconciler.py   # Motor de comparación y detección
│   ├── reporter.py     # Generación de reportes
│   └── main.py         # Punto de entrada
└── requirements.txt
```

## Instalación
```bash
git clone https://github.com/tu-usuario/bank-reconciliation
cd bank-reconciliation
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Uso

### Ejecución manual
```bash
cd src
python3 main.py
```

### Ejecución automatizada con Bash
```bash
bash scripts/run_reconciliation.sh
```

### Programar ejecución diaria (Linux/WSL)
```bash
bash scripts/setup_cron.sh
```

Esto configura el proceso para correr automáticamente cada día a las 2:00am.

## Formato de archivos de entrada

**Reporte del banco** (`data/bank/`):
```csv
transaction_id,date,description,amount,type
TXN001,2024-01-03,PAGO CLIENTE ACME,15000.00,credit
```

**Registros internos** (`data/internal/`):
```csv
transaction_id,date,description,amount,type,account,status
TXN001,2024-01-03,PAGO CLIENTE ACME,15000.00,credit,CTA-001,confirmed
```

## Ejemplo de salida
```
╭──────────────────── Resumen de Conciliación ────────────────────╮
│ Registros banco:      10                                        │
│ Registros internos:   9                                         │
│                                                                 │
│ ✓ Coincidencias:      7                                         │
│ ~ Montos diferentes:  1                                         │
│ ✗ Solo en banco:      2                                         │
│ ✗ Solo internos:      1                                         │
│                                                                 │
│ Total discrepancias: 4                                          │
╰─────────────────────────────────────────────────────────────────╯
```

## Notas técnicas

- El sistema siempre procesa el CSV más reciente de cada carpeta
- Los reportes exportados se guardan con timestamp en `data/processed/`
- Los archivos CSV de datos nunca se versionan en git (datos sensibles)
- `crontab` requiere Linux nativo o WSL con servicio cron activo