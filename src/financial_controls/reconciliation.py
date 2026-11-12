"""Full-universe reconciliation, capped evidence allocations, independent totals."""
from dataclasses import dataclass
import pandas as pd
from .contracts import KEYS, require, unique, normalize_keys

MEASURES = ["lines", "cents"]
EVIDENCE_COLUMNS = [*KEYS, "evidence_id", "rule", "direction", "lines", "cents"]
ALLOCATION_COLUMNS = [*KEYS, "evidence_id", "rule", "direction", "lines", "cents"]


@dataclass
class ControlResult:
    detail: pd.DataFrame
    allocations: pd.DataFrame
    unassigned: pd.DataFrame
    kpis: dict


def summarize(frame):
    require(frame, [*KEYS, *MEASURES])
    clean = normalize_keys(frame)
    return clean.groupby(KEYS, as_index=False, dropna=False)[MEASURES].sum()


def empty_evidence():
    return pd.DataFrame(columns=EVIDENCE_COLUMNS)


def reconcile(expected, actual, evidence=None, unassigned=None, *, tolerance_cents=1):
    if not isinstance(tolerance_cents, int) or tolerance_cents < 0:
        raise ValueError("Tolerance must be nonnegative integer cents")
    for frame in (expected, actual):
        require(frame, [*KEYS, *MEASURES])
        for col in MEASURES:
            if frame[col].isna().any() or not pd.api.types.is_integer_dtype(frame[col]):
                raise ValueError("Measures must be non-null integer units")
        if frame["lines"].lt(0).any():
            raise ValueError("Negative line count")
    # Totals are taken BEFORE joins. Unassigned real amounts stay outside keyed detail.
    unassigned = actual.iloc[0:0].copy() if unassigned is None else unassigned.copy()
    require(unassigned, MEASURES)
    for col in MEASURES:
        if unassigned[col].isna().any() or (
            not unassigned.empty and not pd.api.types.is_integer_dtype(unassigned[col])
        ):
            raise ValueError("Unassigned measures must be integer units")
    if unassigned["lines"].lt(0).any():
        raise ValueError("Negative unassigned line count")
    left, right = summarize(expected), summarize(actual)
    detail = left.merge(right, on=KEYS, how="outer", validate="one_to_one",
                        suffixes=("_expected", "_actual"), indicator="presence")
    for col in [f"{m}_{s}" for m in MEASURES for s in ("expected", "actual")]:
        detail[col] = detail[col].fillna(0).astype("int64")
    for m in MEASURES:
        detail[f"difference_{m}"] = detail[f"{m}_actual"] - detail[f"{m}_expected"]
        detail[f"pending_{m}"] = detail[f"difference_{m}"]
    detail["mixed_direction"] = (
        detail["difference_lines"] * detail["difference_cents"] < 0
    )
    detail["raw_status"] = "OK"
    over = (detail["difference_cents"] > tolerance_cents) | (
        detail["difference_cents"].abs().le(tolerance_cents) & detail["difference_lines"].gt(0)
    )
    under = (detail["difference_cents"] < -tolerance_cents) | (
        detail["difference_cents"].abs().le(tolerance_cents) & detail["difference_lines"].lt(0)
    )
    detail.loc[over, "raw_status"] = "DE MÁS"
    detail.loc[under, "raw_status"] = "DE MENOS"

    evidence = empty_evidence() if evidence is None else evidence.copy()
    require(evidence, EVIDENCE_COLUMNS)
    if not evidence.empty:
        evidence = normalize_keys(evidence)
        for col in ["evidence_id", "rule"]:
            evidence[col] = evidence[col].astype("string").str.strip()
            if evidence[col].isna().any() or evidence[col].eq("").any():
                raise ValueError("Missing justification reference")
        unique(evidence, ["evidence_id"])
        if not evidence["direction"].isin([-1, 1]).all():
            raise ValueError("Invalid justification direction")
        for m in MEASURES:
            if (evidence[m].isna().any() or not pd.api.types.is_integer_dtype(evidence[m])
                    or evidence[m].lt(0).any()):
                raise ValueError("Evidence capacities must be nonnegative integers")
    allocations = []
    # Each evidence row is consumed once, in stable caller-defined priority order.
    for e in evidence.to_dict("records"):
        mask = detail[KEYS].eq(pd.Series({k: e[k] for k in KEYS})).all(axis=1)
        if not mask.any():
            raise ValueError("Justification has no reconciliation key")
        idx = detail.index[mask][0]
        used = {}
        for m in MEASURES:
            pending = int(detail.at[idx, f"pending_{m}"])
            capacity = int(e[m])
            used[m] = min(abs(pending), capacity) if pending * e["direction"] > 0 else 0
            detail.at[idx, f"pending_{m}"] = pending - used[m] * e["direction"]
        allocations.append({**{k: e[k] for k in KEYS}, "evidence_id": e["evidence_id"],
                            "rule": e["rule"], "direction": e["direction"], **used})
    allocations = pd.DataFrame(allocations, columns=ALLOCATION_COLUMNS)
    for m in MEASURES:
        detail[f"justified_{m}"] = detail[f"difference_{m}"] - detail[f"pending_{m}"]
    pending = detail["pending_lines"].ne(0) | detail["pending_cents"].abs().gt(tolerance_cents)
    changed = detail["justified_lines"].ne(0) | detail["justified_cents"].ne(0)
    detail["review_status"] = "OK"
    detail.loc[changed, "review_status"] = "JUSTIFICADO"
    detail.loc[pending, "review_status"] = "PENDIENTE"

    kpis = {"cases": len(detail), "pending_cases": int(pending.sum()),
            "justified_cases": int(detail["review_status"].eq("JUSTIFICADO").sum()),
            "pending_students": int(detail.loc[pending, "student_ref"].nunique()),
            "unassigned_rows": len(unassigned), "tolerance_cents": tolerance_cents}
    for m in MEASURES:
        et = int(expected[m].sum())
        at = int(actual[m].sum()) + int(unassigned[m].sum())
        mother = at - et
        analyzed = int(detail[f"difference_{m}"].sum())
        unallocated = mother - analyzed
        kpis.update({f"expected_{m}": et, f"actual_{m}": at,
                     f"mother_difference_{m}": mother, f"detail_difference_{m}": analyzed,
                     f"unallocated_{m}": unallocated,
                     f"unassigned_{m}": int(unassigned[m].sum()),
                     f"pending_net_{m}": int(detail[f"pending_{m}"].sum()),
                     f"pending_absolute_{m}": int(detail[f"pending_{m}"].abs().sum())})
    kpis["detail_reconciles"] = (
        kpis["unallocated_lines"] == 0 and abs(kpis["unallocated_cents"]) <= tolerance_cents
    )
    kpis["totals_bridge_reconciles"] = all(
        kpis[f"unallocated_{m}"] == kpis[f"unassigned_{m}"] for m in MEASURES
    )
    kpis["control_clear"] = bool(
        not pending.any() and unassigned.empty and kpis["detail_reconciles"]
    )
    return ControlResult(detail.sort_values(KEYS).reset_index(drop=True),
                         allocations, unassigned, kpis)
