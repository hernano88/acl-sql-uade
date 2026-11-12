"""Explicit input contracts. Errors describe categories, never source records."""
import re
import pandas as pd

KEYS = ["student_ref", "program_ref"]


def require(frame, columns):
    if not set(columns).issubset(frame.columns):
        raise ValueError("Missing required columns")


def normalize_keys(frame, *, nullable_program=False):
    require(frame, KEYS)
    clean = frame.copy()
    for key in KEYS:
        clean[key] = clean[key].astype("string").str.strip().str.upper()
        clean[key] = clean[key].mask(clean[key].eq(""), pd.NA)
        if clean[key].isna().any() and not (nullable_program and key == "program_ref"):
            raise ValueError("Missing reconciliation key")
    return clean


def unique(frame, keys):
    require(frame, keys)
    if frame.duplicated(keys).any():
        raise ValueError("Duplicate key violates cardinality contract")


def scope(frame, period, columns, *, nullable_program=False):
    if not isinstance(period, str) or not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period):
        raise ValueError("Period must be YYYY-MM")
    require(frame, ["row_id", "period", *KEYS, *columns])
    clean = normalize_keys(frame, nullable_program=nullable_program)
    clean["row_id"] = clean["row_id"].astype("string").str.strip()
    if clean["row_id"].isna().any() or clean["row_id"].eq("").any():
        raise ValueError("Missing source row identifier")
    unique(clean, ["row_id"])
    if clean["period"].isna().any() or not clean["period"].astype("string").str.fullmatch(
        r"\d{4}-(0[1-9]|1[0-2])"
    ).all():
        raise ValueError("Invalid source period")
    return clean.loc[clean["period"].eq(period)].copy()


def boolean_column(frame, column):
    require(frame, [column])
    values = frame[column].astype("string").str.strip().str.upper()
    if not values.isin(["Y", "N"]).all():
        raise ValueError("Boolean fields require Y or N; null is not a business rule")
    return values.eq("Y")
