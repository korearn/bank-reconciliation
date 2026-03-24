import pandas as pd
from pathlib import Path
from datetime import datetime
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from reconciler import ReconciliationResult

console = Console()


def print_summary_panel(summary: dict) -> None:
    """
    Muestra un panel resumen con los números clave.
    Panel es un componente de Rich que enmarca contenido con un borde.
    """
    total_disc = summary["total_discrepancies"]
    color = "green" if total_disc == 0 else "red"

    content = (
        f"[cyan]Registros banco:[/cyan]      {summary['total_bank']}\n"
        f"[cyan]Registros internos:[/cyan]   {summary['total_internal']}\n\n"
        f"[green]✓ Coincidencias:[/green]      {summary['matched']}\n"
        f"[yellow]~ Montos diferentes:[/yellow]  {summary['amount_mismatch']}\n"
        f"[red]✗ Solo en banco:[/red]       {summary['only_in_bank']}\n"
        f"[red]✗ Solo internos:[/red]       {summary['only_in_internal']}\n\n"
        f"[{color}]Total discrepancias: {total_disc}[/{color}]"
    )

    console.print(Panel(content, title="Resumen de Conciliación", border_style=color))


def print_discrepancy_table(df: pd.DataFrame, title: str, color: str) -> None:
    """Imprime una tabla de discrepancias con Rich."""
    if df.empty:
        console.print(f"[green]✓ Sin discrepancias en: {title}[/green]\n")
        return

    table = Table(title=title, show_lines=True, box=box.ROUNDED)

    for col in df.columns:
        table.add_column(col.replace("_", " ").title(), style=color)

    for _, row in df.iterrows():
        # Formateamos cada celda según su tipo de dato
        formatted = []
        for val in row:
            if isinstance(val, float):
                formatted.append(f"${val:,.2f}")
            elif isinstance(val, pd.Timestamp):
                formatted.append(val.strftime("%Y-%m-%d"))
            else:
                formatted.append(str(val) if pd.notna(val) else "—")
        table.add_row(*formatted)

    console.print(table)
    console.print()


def print_mismatch_table(df: pd.DataFrame) -> None:
    """
    Tabla especial para montos diferentes — muestra ambos montos
    y calcula la diferencia para facilitar la auditoría.
    """
    if df.empty:
        console.print("[green]✓ Sin diferencias de montos[/green]\n")
        return

    table = Table(title="Diferencias de Monto", show_lines=True, box=box.ROUNDED)
    table.add_column("ID",            style="cyan")
    table.add_column("Descripción",   style="white")
    table.add_column("Monto Banco",   style="yellow", justify="right")
    table.add_column("Monto Interno", style="yellow", justify="right")
    table.add_column("Diferencia",    style="red",    justify="right")

    for _, row in df.iterrows():
        diff = row["amount_bank"] - row["amount_internal"]
        desc = row.get("description_bank", row.get("description", "—"))
        table.add_row(
            str(row["transaction_id"]),
            str(desc),
            f"${row['amount_bank']:,.2f}",
            f"${row['amount_internal']:,.2f}",
            f"${diff:,.2f}"
        )

    console.print(table)
    console.print()


def export_report(result: ReconciliationResult, summary: dict, output_dir: Path) -> Path:
    """
    Exporta el reporte completo a un archivo de texto.
    En un proyecto real esto podría ser PDF o un email — la lógica
    de generación es la misma, solo cambia el destino.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = output_dir / f"reconciliation_report_{timestamp}.txt"

    lines = [
        "=" * 60,
        "REPORTE DE CONCILIACIÓN BANCARIA",
        f"Generado: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        "RESUMEN",
        "-" * 40,
        f"Registros banco:       {summary['total_bank']}",
        f"Registros internos:    {summary['total_internal']}",
        f"Coincidencias:         {summary['matched']}",
        f"Diferencias de monto:  {summary['amount_mismatch']}",
        f"Solo en banco:         {summary['only_in_bank']}",
        f"Solo internos:         {summary['only_in_internal']}",
        f"Total discrepancias:   {summary['total_discrepancies']}",
        "",
    ]

    # Agrega cada sección de discrepancias al reporte
    sections = [
        ("DIFERENCIAS DE MONTO", result.amount_mismatch),
        ("SOLO EN BANCO",        result.only_in_bank),
        ("SOLO EN REGISTROS INTERNOS", result.only_in_internal),
    ]

    for title, df in sections:
        lines.append(title)
        lines.append("-" * 40)
        if df.empty:
            lines.append("Sin discrepancias.")
        else:
            lines.append(df.to_string(index=False))
        lines.append("")

    report_path.write_text("\n".join(lines), encoding="utf-8")
    return report_path