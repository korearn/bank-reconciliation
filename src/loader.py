import pandas as pd
from pathlib import Path
from rich.console import Console

console = Console()

# Columnas mínimas que debe tener cada archivo
# Si falta alguna, el programa avisa antes de procesar
REQUIRED_BANK_COLS     = {"transaction_id", "date", "description", "amount", "type"}
REQUIRED_INTERNAL_COLS = {"transaction_id", "date", "description", "amount", "type"}


def load_csv(path: Path, required_cols: set) -> pd.DataFrame:
    """
    Carga un CSV y valida que tenga las columnas necesarias.
    Retorna un DataFrame limpio y listo para procesar.
    """
    if not path.exists():
        raise FileNotFoundError(f"No se encontró el archivo: {path}")

    df = pd.read_csv(path)

    # Validación de columnas — detecta errores de formato temprano
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Columnas faltantes en {path.name}: {missing}")

    # Limpieza básica — strip elimina espacios al inicio y final de strings
    df["transaction_id"] = df["transaction_id"].str.strip()
    df["description"]    = df["description"].str.strip()
    df["amount"]         = pd.to_numeric(df["amount"], errors="coerce")
    df["date"]           = pd.to_datetime(df["date"], errors="coerce")

    # Reporta filas con montos inválidos si las hay
    invalid = df[df["amount"].isna()]
    if not invalid.empty:
        console.print(f"[yellow]Advertencia:[/yellow] {len(invalid)} filas con monto inválido en {path.name}")

    console.print(f"[green]✓[/green] {path.name} — {len(df)} registros cargados")
    return df


def load_bank_report(path: Path) -> pd.DataFrame:
    """Carga el reporte del banco."""
    return load_csv(path, REQUIRED_BANK_COLS)


def load_internal_records(path: Path) -> pd.DataFrame:
    """Carga los registros internos."""
    return load_csv(path, REQUIRED_INTERNAL_COLS)