import pandas as pd
from dataclasses import dataclass
from typing import Optional

@dataclass
class ReconciliationResult:
    """
    dataclass es una forma moderna de crear clases que solo guardan datos.
    Es más limpio que un diccionario porque tiene tipos definidos y
    autocompletado.
    """
    matched:        pd.DataFrame  # Transacciones que coinciden perfectamente
    amount_mismatch: pd.DataFrame  # Misma ID pero montos diferentes
    only_in_bank:   pd.DataFrame  # En banco pero no en registros internos
    only_in_internal: pd.DataFrame  # En registros internos pero no en banco


def reconcile(bank_df: pd.DataFrame, internal_df: pd.DataFrame) -> ReconciliationResult:
    """
    Compara dos DataFrames y clasifica cada transacción.

    La estrategia es usar 'transaction_id' como llave de unión —
    igual que un JOIN en SQL. Pandas tiene merge() que hace exactamente eso.
    """

    # outer join: incluye TODAS las filas de ambos DataFrames
    # aunque no tengan pareja en el otro lado
    # suffixes distingue columnas con el mismo nombre de cada fuente
    merged = pd.merge(
        bank_df[["transaction_id", "date", "description", "amount", "type"]],
        internal_df[["transaction_id", "date", "description", "amount", "type"]],
        on="transaction_id",
        how="outer",
        suffixes=("_bank", "_internal")
    )

    # Transacciones que solo existen en el banco
    # (amount_internal es NaN porque no tuvo pareja en internal)
    only_in_bank = merged[merged["amount_internal"].isna()].copy()
    only_in_bank = only_in_bank[["transaction_id", "date_bank", "description_bank", "amount_bank", "type_bank"]]
    only_in_bank.columns = ["transaction_id", "date", "description", "amount", "type"]

    # Transacciones que solo existen internamente
    only_in_internal = merged[merged["amount_bank"].isna()].copy()
    only_in_internal = only_in_internal[["transaction_id", "date_internal", "description_internal", "amount_internal", "type_internal"]]
    only_in_internal.columns = ["transaction_id", "date", "description", "amount", "type"]

    # Transacciones que existen en ambos lados
    both = merged[merged["amount_bank"].notna() & merged["amount_internal"].notna()].copy()

    # De las que existen en ambos, separa las que tienen montos diferentes
    # round(2) evita falsos positivos por decimales flotantes (ej: 100.0 vs 99.9999999)
    amount_mismatch = both[
        both["amount_bank"].round(2) != both["amount_internal"].round(2)
    ].copy()

    # Las que coinciden perfectamente
    matched = both[
        both["amount_bank"].round(2) == both["amount_internal"].round(2)
    ].copy()

    return ReconciliationResult(
        matched=matched,
        amount_mismatch=amount_mismatch,
        only_in_bank=only_in_bank,
        only_in_internal=only_in_internal
    )


def get_summary(result: ReconciliationResult, bank_df: pd.DataFrame, internal_df: pd.DataFrame) -> dict:
    """Calcula métricas generales del proceso de conciliación."""
    return {
        "total_bank":          len(bank_df),
        "total_internal":      len(internal_df),
        "matched":             len(result.matched),
        "amount_mismatch":     len(result.amount_mismatch),
        "only_in_bank":        len(result.only_in_bank),
        "only_in_internal":    len(result.only_in_internal),
        "total_discrepancies": len(result.amount_mismatch) + len(result.only_in_bank) + len(result.only_in_internal)
    }