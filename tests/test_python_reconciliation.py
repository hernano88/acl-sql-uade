from pathlib import Path

import pandas as pd

from python_jupyter.src.control_reconciliation import (
    build_control_kpis,
    reconcile_scopes,
)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _load_control():
    expected = pd.read_csv(REPO_ROOT / "data" / "synthetic_expected_scope.csv")
    billed = pd.read_csv(REPO_ROOT / "data" / "synthetic_billed_scope.csv")
    return reconcile_scopes(expected, billed)


def test_detects_differences_in_both_directions():
    control = _load_control().set_index("account_ref")

    assert control.loc["ACC-1006", "difference_direction"] == (
        "EXPECTED_WITHOUT_BILLING"
    )
    assert control.loc["ACC-1007", "difference_direction"] == (
        "BILLED_WITHOUT_EXPECTED"
    )
    assert control.loc["ACC-1004", "status"] == "JUSTIFIED"
    assert control.loc["ACC-1005", "status"] == "JUSTIFIED"


def test_builds_line_amount_and_exception_checks():
    kpis = build_control_kpis(_load_control())

    # Total line counts offset each other, while the outer join still exposes
    # one missing and one unexpected account. This is why totals alone are not
    # a sufficient reconciliation control.
    assert kpis["expected_lines"] == 10
    assert kpis["actual_lines"] == 10
    assert kpis["expected_amount"] == 98_000
    assert kpis["actual_amount"] == 92_500
    assert kpis["pending_accounts"] == 2
