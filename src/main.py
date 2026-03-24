import sys
from pathlib import Path
from rich.console import Console

# src/ al path para que los imports funcionen
# cuando el script se ejecuta desde scripts/run_reconciliation.sh
sys.path.insert(0, str(Path(__file__).parent))

from loader import load_bank_report, load_internal_records
from reconciler import reconcile, get_summary
from reporter import (
    print_summary_panel,
    print_discrepancy_table,
    print_mismatch_table,
    export_report
)

console = Console()

# Rutas relativas a la raíz del proyecto
ROOT        = Path(__file__).parent.parent
BANK_DIR    = ROOT / "data" / "bank"
INTERNAL_DIR = ROOT / "data" / "internal"
OUTPUT_DIR  = ROOT / "data" / "processed"


def find_latest_file(directory: Path, pattern: str = "*.csv") -> Path:
    """
    Encuentra el CSV más reciente en un directorio.
    sorted() + key=stat().st_mtime ordena por fecha de modificación.
    Esto simula cómo un sistema real procesaría el archivo más nuevo del banco.
    """
    files = list(directory.glob(pattern))
    if not files:
        raise FileNotFoundError(f"No hay archivos CSV en {directory}")
    return sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)[0]


def main():
    console.rule("[bold blue]BANK RECONCILIATION[/bold blue]")

    # 1. Cargar archivos
    console.print("\n[bold]Paso 1:[/bold] Cargando archivos...\n")
    bank_path     = find_latest_file(BANK_DIR)
    internal_path = find_latest_file(INTERNAL_DIR)

    bank_df     = load_bank_report(bank_path)
    internal_df = load_internal_records(internal_path)

    # 2. Reconciliar
    console.print("\n[bold]Paso 2:[/bold] Ejecutando conciliación...\n")
    result  = reconcile(bank_df, internal_df)
    summary = get_summary(result, bank_df, internal_df)

    # 3. Mostrar resultados
    console.print("\n[bold]Paso 3:[/bold] Resultados\n")
    print_summary_panel(summary)

    console.print("\n[bold]Diferencias de monto:[/bold]")
    print_mismatch_table(result.amount_mismatch)

    console.print("[bold]Solo en banco:[/bold]")
    print_discrepancy_table(result.only_in_bank, "Transacciones solo en banco", "red")

    console.print("[bold]Solo en registros internos:[/bold]")
    print_discrepancy_table(result.only_in_internal, "Solo en registros internos", "yellow")

    # 4. Exportar reporte
    console.print("\n[bold]Paso 4:[/bold] Exportando reporte...\n")
    report_path = export_report(result, summary, OUTPUT_DIR)
    console.print(f"[green]✓[/green] Reporte guardado en: {report_path}")

    console.rule("[bold blue]Proceso completado[/bold blue]")


if __name__ == "__main__":
    main()