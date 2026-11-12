"""Three synthetic controls. Business assumptions are documented in docs/business_rules.md."""
import pandas as pd
from .contracts import KEYS, scope, unique, require, boolean_column
from .money import money_column, rate_amount
from .reconciliation import reconcile, empty_evidence
from .trace import scoped, record


def units(frame, *, money=False):
    clean = frame.copy()
    clean["lines"] = pd.Series(1, index=clean.index, dtype="int64")
    clean["cents"] = money_column(clean["amount"]) if money else pd.Series(
        0, index=clean.index, dtype="int64"
    )
    return clean


def evidence_from(frame, rule, direction, *, money=False):
    if frame.empty:
        return empty_evidence()
    result = units(frame, money=money)[[*KEYS, "row_id", "lines", "cents"]].copy()
    result = result.rename(columns={"row_id": "evidence_id"})
    result["evidence_id"] = rule + ":" + result["evidence_id"]
    result["rule"], result["direction"] = rule, direction
    if money:
        # Evidence is a capacity, not a signed accounting movement.
        if result["cents"].lt(0).any():
            raise ValueError("Negative adjustment capacity requires explicit review")
    return result


def enrollment_control(enrollments, assigned, cash, *, period):
    enr = scope(enrollments, period, ["chargeable"])
    asg = scope(assigned, period, ["prior_period"])
    cash_input = cash
    cash = scope(cash, period, [])
    stages = []
    for name, original, selected in [("enrollments", enrollments, enr), ("assigned", assigned, asg), ("cash", cash_input, cash)]:
        scoped(stages, name, original, selected)
    chargeable = boolean_column(enr, "chargeable")
    prior = boolean_column(asg, "prior_period")
    evidence = pd.concat([
        evidence_from(cash, "SYNTHETIC_CASH", -1),
        evidence_from(enr.loc[~chargeable], "SYNTHETIC_NON_CHARGEABLE", -1),
        evidence_from(asg.loc[prior], "SYNTHETIC_PRIOR_PERIOD", 1),
    ], ignore_index=True)
    result = reconcile(units(enr), units(asg), evidence)
    result.trace = stages + result.trace
    return result


def billing_control(assigned, billed, *, period):
    billed_input = billed
    asg = scope(assigned, period, ["amount"])
    billed = scope(billed, period, ["amount", "manual_adjustment"])
    stages = []
    scoped(stages, "assigned", assigned, asg)
    scoped(stages, "billed", billed_input, billed)
    manual = boolean_column(billed, "manual_adjustment")
    evidence = evidence_from(billed.loc[manual], "SYNTHETIC_MANUAL_ADJUSTMENT", 1, money=True)
    result = reconcile(units(asg, money=True), units(billed, money=True), evidence)
    result.trace = stages + result.trace
    return result


def scholarship_control(enrollments, billed, applied, rules, exceptions, *, period):
    billed_input, applied_input, exceptions_input = billed, applied, exceptions
    enr = scope(enrollments, period, ["chargeable"])
    boolean_column(enr, "chargeable")
    billed = scope(billed, period, ["amount"])
    applied = scope(applied, period, ["amount"], nullable_program=True)
    stages = []
    scoped(stages, "enrollments", enrollments, enr)
    scoped(stages, "billed", billed_input, billed)
    scoped(stages, "applied", applied_input, applied)
    require(rules, ["period", "program_ref", "min_subjects", "rate_bps"])
    rules = rules.loc[rules["period"].eq(period)].copy()
    rules["program_ref"] = rules["program_ref"].astype("string").str.strip().str.upper()
    if rules["program_ref"].isna().any() or rules["program_ref"].eq("").any():
        raise ValueError("Missing rule key")
    unique(rules, ["program_ref"])
    for col in ["min_subjects", "rate_bps"]:
        numeric = pd.to_numeric(rules[col], errors="coerce")
        if numeric.isna().any() or numeric.mod(1).ne(0).any():
            raise ValueError("Rule values must be integers")
        rules[col] = numeric.astype("int64")
    if rules["min_subjects"].lt(1).any() or not rules["rate_bps"].between(0, 10000).all():
        raise ValueError("Invalid synthetic eligibility rule")

    record(stages, "eligibility.rules", len(rules), "many_to_one;no_missing_configuration")
    base = units(billed, money=True).groupby(KEYS, as_index=False)["cents"].sum()
    counts = enr.groupby(KEYS, as_index=False).size().rename(columns={"size": "subjects"})
    theory = base.merge(rules[["program_ref", "min_subjects", "rate_bps"]],
                        on="program_ref", how="left", validate="many_to_one", indicator=True)
    if theory["_merge"].ne("both").any():
        raise ValueError("Missing scholarship configuration; no silent default")
    theory = theory.drop(columns="_merge").merge(
        counts, on=KEYS, how="left", validate="one_to_one"
    )
    theory["subjects"] = theory["subjects"].fillna(0).astype("int64")
    if theory["cents"].lt(0).any():
        raise ValueError("Negative scholarship base requires explicit review")
    theory["base_cents"] = theory["cents"]
    theory["cents"] = pd.Series([
        rate_amount(r.cents, r.rate_bps) if r.subjects >= r.min_subjects else 0
        for r in theory.itertuples()
    ], index=theory.index, dtype="int64")
    theory["lines"] = pd.Series(0, index=theory.index, dtype="int64")
    record(stages, "eligibility.theory", len(theory), "one_to_one_counts;half_up_rate")
    real = units(applied, money=True)
    if real["cents"].lt(0).any():
        raise ValueError("Applied scholarship must use positive benefit convention")
    real["lines"] = 0  # Scholarship reconciliation measures money, not benefit row counts.
    unassigned = real.loc[real["program_ref"].isna()].copy()
    record(stages, "route.unassigned", len(unassigned), "never_distribute_across_programs")
    assigned_real = real.loc[real["program_ref"].notna()].copy()

    exc = scope(exceptions, period, ["rule", "direction", "amount"])
    scoped(stages, "exceptions", exceptions_input, exc)
    if not exc["rule"].astype("string").str.startswith("SYNTHETIC_").all():
        raise ValueError("Public exception rules must be explicitly synthetic")
    evidence = evidence_from(exc, "SYNTHETIC_SCHOLARSHIP_EXCEPTION", 1, money=True)
    evidence["rule"] = exc["rule"].values
    directions = pd.to_numeric(exc["direction"], errors="coerce")
    if not directions.isin([-1, 1]).all():
        raise ValueError("Invalid scholarship exception direction")
    evidence["direction"] = directions.astype("int64").values
    evidence["lines"] = pd.Series(0, index=evidence.index, dtype="int64")
    result = reconcile(theory, assigned_real, evidence, unassigned)
    result.detail = result.detail.merge(
        theory[[*KEYS, "subjects", "min_subjects", "rate_bps", "base_cents"]],
        on=KEYS, how="left", validate="one_to_one"
    )
    result.trace = stages + result.trace
    return result
