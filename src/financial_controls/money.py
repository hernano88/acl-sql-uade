"""Decimal ingestion, integer-cent arithmetic, explicit half-up rounding."""
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
import pandas as pd


def cents(value):
    if value is None or pd.isna(value) or isinstance(value, bool):
        raise ValueError("Missing or invalid monetary value")
    try:
        number = Decimal(str(value))
        if not number.is_finite():
            raise ValueError("Non-finite monetary value")
        result = int((number * 100).quantize(Decimal("1"), rounding=ROUND_HALF_UP))
    except (InvalidOperation, ValueError, TypeError):
        raise ValueError("Invalid monetary value") from None
    if abs(result) > 10**12:
        raise ValueError("Monetary value exceeds public-demo limit")
    return result


def money_column(series):
    return series.map(cents).astype("int64")


def rate_amount(base_cents, rate_bps):
    return int((Decimal(int(base_cents)) * Decimal(int(rate_bps)) / 10000).quantize(
        Decimal("1"), rounding=ROUND_HALF_UP
    ))


def format_cents(value):
    value = int(value)
    sign = "-" if value < 0 else ""
    return f"{sign}{abs(value) // 100:,}.{abs(value) % 100:02d}"
