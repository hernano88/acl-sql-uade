from pathlib import Path
import pandas as pd
import pytest
from financial_controls.contracts import normalize_keys
from financial_controls.money import cents, rate_amount, format_cents
from financial_controls.reconciliation import reconcile, empty_evidence
from financial_controls.demo import run_cases, load_inputs
from financial_controls.controls import enrollment_control, billing_control, scholarship_control
from financial_controls.reporting import render_html

ROOT = Path(__file__).resolve().parents[1]


def frame(rows):
    return pd.DataFrame(rows, columns=["student_ref", "program_ref", "lines", "cents"]).astype(
        {"lines": "int64", "cents": "int64"}
    )


def one(lines=1, money=10000, student="SYN-S001", program="SYN-A"):
    return frame([(student, program, lines, money)])


def evidence(lines=1, money=10000, direction=1):
    return pd.DataFrame([{
        "student_ref": "SYN-S001", "program_ref": "SYN-A", "evidence_id": "SYN-X",
        "rule": "SYNTHETIC_RULE", "direction": direction, "lines": lines, "cents": money
    }])


@pytest.mark.parametrize("value,expected", [("1.005", 101), ("-1.005", -101),
                                           ("0.10", 10), ("10", 1000)])
def test_decimal_ingestion(value, expected):
    assert cents(value) == expected


@pytest.mark.parametrize("value", [None, "", "NaN", "Infinity", "invalid", True, 10**20])
def test_invalid_money_rejected(value):
    with pytest.raises(ValueError):
        cents(value)


def test_rate_rounding_and_signed_display():
    assert rate_amount(105, 1000) == 11
    assert format_cents(-105) == "-1.05"


def test_keys_normalize_without_losing_leading_zeroes():
    result = normalize_keys(pd.DataFrame({"student_ref": [" 001 "], "program_ref": [" syn-a "]}))
    assert result.iloc[0].tolist() == ["001", "SYN-A"]


@pytest.mark.parametrize("value", [None, "", "  "])
def test_missing_keys_rejected(value):
    with pytest.raises(ValueError):
        normalize_keys(pd.DataFrame({"student_ref": [value], "program_ref": ["SYN-A"]}))


def test_composite_key_prevents_cross_program_compensation():
    result = reconcile(one(program="SYN-A"), one(program="SYN-B"))
    assert result.kpis["mother_difference_cents"] == 0
    assert result.kpis["pending_absolute_cents"] == 20000
    assert set(result.detail.raw_status) == {"DE MÁS", "DE MENOS"}
    assert result.kpis["pending_cases"] == 2


def test_count_only_difference_and_mixed_direction():
    result = reconcile(one(2, 100), one(1, 100))
    assert result.detail.iloc[0].raw_status == "DE MENOS"
    mixed = reconcile(one(2, 100), one(1, 200))
    assert bool(mixed.detail.iloc[0].mixed_direction)
    assert mixed.detail.iloc[0].review_status == "PENDIENTE"


def test_partial_justification_is_capped_and_original_kept():
    result = reconcile(one(1, 10000), one(3, 30000), evidence(1, 5000))
    row = result.detail.iloc[0]
    assert (row.difference_lines, row.difference_cents) == (2, 20000)
    assert (row.justified_lines, row.justified_cents) == (1, 5000)
    assert (row.pending_lines, row.pending_cents) == (1, 15000)
    assert row.review_status == "PENDIENTE"
    capped = reconcile(one(), one(2, 20000), evidence(100, 999999))
    assert capped.detail.iloc[0].pending_cents == 0
    assert capped.detail.iloc[0].review_status == "JUSTIFICADO"


def test_duplicate_evidence_is_not_consumed_twice():
    duplicated = pd.concat([evidence(), evidence()], ignore_index=True)
    with pytest.raises(ValueError, match="cardinality"):
        reconcile(one(), one(2, 20000), duplicated)


def test_opposite_direction_evidence_does_not_hide_difference():
    result = reconcile(one(2, 20000), one(), evidence(direction=1))
    assert result.detail.iloc[0].pending_cents == -10000


def test_unassigned_is_not_replicated_for_multiple_programs():
    expected = pd.concat([one(), one(program="SYN-B")], ignore_index=True)
    real = expected.copy()
    orphan = one(0, 300)
    orphan["program_ref"] = pd.NA
    result = reconcile(expected, real, unassigned=orphan)
    assert result.kpis["unallocated_cents"] == 300
    assert result.kpis["actual_cents"] == 20300
    assert not result.kpis["detail_reconciles"]
    assert result.kpis["totals_bridge_reconciles"]
    assert not result.kpis["control_clear"]


def test_signed_reversals_are_preserved():
    expected = pd.concat([one(1, 10000), one(1, -10000)], ignore_index=True)
    result = reconcile(expected, one(2, 0))
    assert result.kpis["expected_cents"] == 0
    assert result.kpis["control_clear"]


def test_tolerance_does_not_erase_original_residuals():
    result = reconcile(one(1, 100), one(1, 101))
    assert result.detail.iloc[0].difference_cents == 1
    assert result.detail.iloc[0].raw_status == "OK"
    assert result.kpis["pending_absolute_cents"] == 1
    assert result.kpis["detail_reconciles"]


def test_empty_scopes_are_valid():
    empty = frame([])
    result = reconcile(empty, empty)
    assert result.kpis["control_clear"]
    assert result.detail.empty


def test_measure_contract():
    with pytest.raises(ValueError):
        reconcile(one().astype({"cents": "float64"}), one())


@pytest.mark.parametrize("period", ["2030-01", "2030-02"])
def test_off_season_has_explicit_empty_result(period):
    cases = run_cases(ROOT, period)
    assert all(result.kpis["cases"] == 0 for result in cases.values())


@pytest.mark.parametrize("period", ["2030-13", "2030", None])
def test_invalid_period_rejected(period):
    with pytest.raises(ValueError):
        run_cases(ROOT, period)


def scholarship_args():
    data = load_inputs(ROOT)
    return [data[n] for n in ("enrollments", "billed", "scholarships",
                              "scholarship_rules", "scholarship_exceptions")]


def test_duplicate_rule_fails_before_many_to_one_join():
    args = scholarship_args()
    args[3] = pd.concat([args[3], args[3].iloc[[0]]], ignore_index=True)
    with pytest.raises(ValueError, match="cardinality"):
        scholarship_control(*args, period="2030-09")


def test_missing_configuration_has_no_silent_default():
    args = scholarship_args()
    args[3] = args[3].iloc[0:0]
    with pytest.raises(ValueError, match="configuration"):
        scholarship_control(*args, period="2030-09")


def test_duplicate_source_row_rejected():
    data = load_inputs(ROOT)
    data["assigned"] = pd.concat([data["assigned"], data["assigned"].iloc[[0]]])
    with pytest.raises(ValueError, match="cardinality"):
        billing_control(data["assigned"], data["billed"], period="2030-09")


def test_null_chargeability_is_not_automatically_justified():
    data = load_inputs(ROOT)
    data["enrollments"].loc[0, "chargeable"] = ""
    with pytest.raises(ValueError, match="Boolean"):
        enrollment_control(data["enrollments"], data["assigned"], data["cash"], period="2030-09")


def test_negative_applied_benefit_requires_review():
    args = scholarship_args()
    args[2].loc[0, "amount"] = "-20.00"
    with pytest.raises(ValueError, match="positive benefit"):
        scholarship_control(*args, period="2030-09")


def test_fixture_results_independently_known():
    enrollment, billing, scholarship = run_cases(ROOT).values()
    assert (enrollment.kpis["expected_lines"], enrollment.kpis["actual_lines"]) == (10, 9)
    assert enrollment.kpis["pending_cases"] == 2
    assert (billing.kpis["expected_cents"], billing.kpis["actual_cents"]) == (93000, 89000)
    assert billing.kpis["mother_difference_cents"] == -4000
    assert billing.kpis["pending_net_cents"] == -23000
    assert billing.kpis["pending_absolute_cents"] == 23000
    assert billing.kpis["pending_cases"] == 2
    assert (scholarship.kpis["expected_cents"], scholarship.kpis["actual_cents"]) == (4500, 6500)
    assert scholarship.kpis["detail_difference_cents"] == 1700
    assert scholarship.kpis["unallocated_cents"] == 300
    assert scholarship.kpis["pending_net_cents"] == 1200
    assert scholarship.kpis["pending_absolute_cents"] == 1200
    detail = scholarship.detail.set_index(["student_ref", "program_ref"])
    assert detail.loc[("SYN-S005", "SYN-A"), "presence"] == "right_only"
    assert detail.loc[("SYN-S001", "SYN-A"), "cents_actual"] == 2000
    assert detail.loc[("SYN-S001", "SYN-B"), "cents_actual"] == 0


def test_allocations_bridge_each_original_difference():
    for result in run_cases(ROOT).values():
        for m in ["lines", "cents"]:
            assert (result.detail[f"difference_{m}"] ==
                    result.detail[f"justified_{m}"] + result.detail[f"pending_{m}"]).all()
            assert result.kpis[f"mother_difference_{m}"] == (
                result.kpis[f"detail_difference_{m}"] + result.kpis[f"unassigned_{m}"]
            )


def test_html_escapes_labels():
    result = reconcile(one(), one())
    result.detail.loc[0, "student_ref"] = "<script>alert(1)</script>"
    html = render_html(result, "<test>")
    assert "<script>" not in html and "&lt;test&gt;" in html


def test_oracle_template_is_inert_on_import(monkeypatch):
    import runpy
    for name in ["ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]:
        monkeypatch.delenv(name, raising=False)
    module = runpy.run_path(str(ROOT / "examples" / "oracle_connection.py"))
    assert callable(module["extract_synthetic_scopes"])


def test_evidence_without_key_fails():
    wrong = evidence()
    wrong["student_ref"] = "SYN-UNKNOWN"
    with pytest.raises(ValueError, match="no reconciliation key"):
        reconcile(one(), one(), wrong)


def test_no_case_passes_with_only_one_dimension_closed():
    result = reconcile(one(1, 10000), one(2, 20000), evidence(1, 5000))
    assert result.detail.iloc[0].pending_lines == 0
    assert result.detail.iloc[0].pending_cents == 5000
    assert result.detail.iloc[0].review_status == "PENDIENTE"


def test_missing_input_column_is_explicit():
    with pytest.raises(ValueError, match="required columns"):
        billing_control(pd.DataFrame(), pd.DataFrame(), period="2030-09")


def test_invalid_rule_value_does_not_echo_source_value():
    args = scholarship_args()
    args[3].loc[0, "rate_bps"] = "SYN-INVALID-RATE"
    with pytest.raises(ValueError) as caught:
        scholarship_control(*args, period="2030-09")
    assert "SYN-INVALID-RATE" not in str(caught.value)


def test_negative_unassigned_line_count_rejected():
    with pytest.raises(ValueError, match="Negative unassigned"):
        reconcile(one(), one(), unassigned=one(-1, 0))


def test_stage_trace_is_ordered_and_metadata_only(caplog):
    import logging
    caplog.set_level(logging.INFO, logger="financial_controls")
    for result in run_cases(ROOT).values():
        stages = [event["stage"] for event in result.trace]
        assert stages[0].startswith("scope.")
        assert stages[-1] == "totals_bridge"
        assert stages.index("input_contract") < stages.index("join.outer")
        assert stages.index("join.outer") < stages.index("allocate_evidence")
        assert result.trace[-1]["check"] == "PASS"
    assert "SYN-S001" not in caplog.text
    assert "stage=join.outer" in caplog.text


def test_summary_preserves_amounts_and_case_counts():
    from financial_controls.reporting import summarize_review
    for result in run_cases(ROOT).values():
        summary = summarize_review(result)
        assert summary["cases"].sum() == len(result.detail)
        assert summary["difference_cents"].sum() == result.kpis["detail_difference_cents"]
        assert summary["pending_cents"].sum() == result.kpis["pending_net_cents"]


def test_review_export_contains_stage_ledger(tmp_path):
    from financial_controls.reporting import export_review
    result = run_cases(ROOT)["03_scholarship"]
    export_review(result, tmp_path, "Synthetic scholarship")
    trace = pd.read_csv(tmp_path / "trace.csv")
    assert trace.iloc[-1]["stage"] == "totals_bridge"
    assert (tmp_path / "summary.csv").is_file()
    assert "3.00" in (tmp_path / "report.html").read_text(encoding="utf-8")
