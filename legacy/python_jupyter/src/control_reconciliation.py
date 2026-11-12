"""Synthetic billing-control logic.

The module reproduces the technical pattern of selected professional controls
without exposing production schemas, identifiers, rules, or data.
"""

from __future__ import annotations

import pandas as pd


NUMERIC_COLUMNS = [
    "expected_line_count",
    "expected_amount",
    "base_line_count",
    "base_amount",
    "justified_line_count",
    "justified_amount",
    "actual_line_count",
    "actual_amount",
]


def _normalize_account_ref(series: pd.Series) -> pd.Series:
    """Return stable string identifiers and remove accidental whitespace."""

    return series.astype("string").str.strip().str.upper()


def _summarize_expected(expected: pd.DataFrame) -> pd.DataFrame:
    required = {"account_ref", "expected_line_count", "expected_amount"}
    missing = required.difference(expected.columns)
    if missing:
        raise ValueError(f"Missing expected-scope columns: {sorted(missing)}")

    clean = expected.copy()
    clean["account_ref"] = _normalize_account_ref(clean["account_ref"])
    return (
        clean.groupby("account_ref", as_index=False)
        .agg(
            expected_line_count=("expected_line_count", "sum"),
            expected_amount=("expected_amount", "sum"),
        )
    )


def _summarize_billed(billed: pd.DataFrame) -> pd.DataFrame:
    required = {
        "account_ref",
        "billed_line_count",
        "billed_amount",
        "justification_type",
    }
    missing = required.difference(billed.columns)
    if missing:
        raise ValueError(f"Missing billed-scope columns: {sorted(missing)}")

    clean = billed.copy()
    clean["account_ref"] = _normalize_account_ref(clean["account_ref"])
    clean["justification_type"] = (
        clean["justification_type"].astype("string").str.strip().str.upper()
    )
    clean["is_justification"] = clean["justification_type"].ne("NONE")
    clean["base_line_count"] = clean["billed_line_count"].where(
        ~clean["is_justification"], 0
    )
    clean["base_amount"] = clean["billed_amount"].where(
        ~clean["is_justification"], 0
    )
    clean["justified_line_count"] = clean["billed_line_count"].where(
        clean["is_justification"], 0
    )
    clean["justified_amount"] = clean["billed_amount"].where(
        clean["is_justification"], 0
    )

    return (
        clean.groupby("account_ref", as_index=False)
        .agg(
            base_line_count=("base_line_count", "sum"),
            base_amount=("base_amount", "sum"),
            justified_line_count=("justified_line_count", "sum"),
            justified_amount=("justified_amount", "sum"),
        )
        .assign(
            actual_line_count=lambda frame: (
                frame["base_line_count"] + frame["justified_line_count"]
            ),
            actual_amount=lambda frame: (
                frame["base_amount"] + frame["justified_amount"]
            ),
        )
    )


def reconcile_scopes(
    expected: pd.DataFrame,
    billed: pd.DataFrame,
    *,
    amount_tolerance: float = 0.01,
) -> pd.DataFrame:
    """Outer-join both universes and classify every account-level difference.

    A full outer join is intentional: it detects both expected-but-not-billed
    and billed-without-expected records. Aggregate totals alone could hide those
    offsetting exceptions.
    """

    expected_summary = _summarize_expected(expected)
    billed_summary = _summarize_billed(billed)
    control = expected_summary.merge(billed_summary, on="account_ref", how="outer")
    control[NUMERIC_COLUMNS] = control[NUMERIC_COLUMNS].fillna(0)

    control["line_difference"] = (
        control["expected_line_count"] - control["actual_line_count"]
    )
    control["amount_difference"] = (
        control["expected_amount"] - control["actual_amount"]
    )
    control["base_line_difference"] = (
        control["expected_line_count"] - control["base_line_count"]
    )
    control["base_amount_difference"] = (
        control["expected_amount"] - control["base_amount"]
    )

    line_matches = control["line_difference"].eq(0)
    amount_matches = control["amount_difference"].abs().le(amount_tolerance)
    has_justification = (
        control["justified_line_count"].gt(0)
        | control["justified_amount"].abs().gt(amount_tolerance)
    )
    fully_matched = line_matches & amount_matches

    control["status"] = "PENDING_REVIEW"
    control.loc[fully_matched & ~has_justification, "status"] = "RECONCILED"
    control.loc[fully_matched & has_justification, "status"] = "JUSTIFIED"

    control["difference_direction"] = "MATCH"
    control.loc[
        control["expected_line_count"].gt(0) & control["actual_line_count"].eq(0),
        "difference_direction",
    ] = "EXPECTED_WITHOUT_BILLING"
    control.loc[
        control["expected_line_count"].eq(0) & control["actual_line_count"].gt(0),
        "difference_direction",
    ] = "BILLED_WITHOUT_EXPECTED"
    control.loc[
        control["status"].eq("PENDING_REVIEW")
        & control["difference_direction"].eq("MATCH"),
        "difference_direction",
    ] = "COUNT_OR_AMOUNT_MISMATCH"
    control.loc[
        control["status"].eq("JUSTIFIED"), "difference_direction"
    ] = "MATCH_AFTER_JUSTIFICATION"

    return control.sort_values(["status", "account_ref"]).reset_index(drop=True)


def build_control_kpis(control: pd.DataFrame) -> dict[str, float | int]:
    """Build line, amount, and exception checks for a compact dashboard."""

    return {
        "expected_lines": int(control["expected_line_count"].sum()),
        "actual_lines": int(control["actual_line_count"].sum()),
        "expected_amount": float(control["expected_amount"].sum()),
        "actual_amount": float(control["actual_amount"].sum()),
        "reconciled_accounts": int(control["status"].eq("RECONCILED").sum()),
        "justified_accounts": int(control["status"].eq("JUSTIFIED").sum()),
        "pending_accounts": int(control["status"].eq("PENDING_REVIEW").sum()),
    }
