"""Review summaries, escaped dashboard and portable exports. All amounts retain signs."""
from html import escape
from pathlib import Path
import json
import pandas as pd
from .money import format_cents


def summarize_review(result):
    return result.detail.groupby(["raw_status", "review_status"], as_index=False).agg(
        cases=("student_ref", "size"), students=("student_ref", "nunique"),
        difference_lines=("difference_lines", "sum"),
        difference_cents=("difference_cents", "sum"),
        justified_cents=("justified_cents", "sum"),
        pending_cents=("pending_cents", "sum")
    )


def display_detail(result):
    columns = ["student_ref", "program_ref", "lines_expected", "lines_actual",
               "cents_expected", "cents_actual", "difference_lines", "difference_cents",
               "justified_cents", "pending_cents", "raw_status", "review_status", "presence"]
    view = result.detail[columns].copy()
    for col in list(view):
        if "cents" in col:
            view[col] = view[col].map(format_cents)
    view = view.rename(columns={col: col.replace("cents", "amount") for col in view if "cents" in col})
    return view


def render_html(result, title):
    k = result.kpis
    cards = [
        ("Expected amount", format_cents(k["expected_cents"])),
        ("Actual incl. unassigned", format_cents(k["actual_cents"])),
        ("Pending keyed cases", k["pending_cases"]),
        ("Absolute keyed pending", format_cents(k["pending_absolute_cents"])),
        ("Unassigned amount", format_cents(k["unassigned_cents"])),
    ]
    card_html = "".join(f"<div class='card'><span>{escape(label)}</span><strong>{escape(str(value))}</strong></div>"
                        for label, value in cards)
    summary = summarize_review(result)
    for col in ["difference_cents", "justified_cents", "pending_cents"]:
        summary[col.replace("cents", "amount")] = summary.pop(col).map(format_cents)
    bridge = pd.DataFrame([
        {"measure": m, "expected": k[f"expected_{m}"], "actual": k[f"actual_{m}"],
         "mother_difference": k[f"mother_difference_{m}"],
         "keyed_detail": k[f"detail_difference_{m}"], "unassigned": k[f"unassigned_{m}"],
         "unallocated": k[f"unallocated_{m}"]} for m in ["lines", "cents"]
    ])
    state = "CLEAR" if k["control_clear"] else "REVIEW REQUIRED"
    table = lambda frame: "<div class='table-wrap'>" + frame.to_html(index=False, escape=True) + "</div>"
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'><meta name='viewport' content='width=device-width'>"
        "<title>" + escape(title) + "</title><style>"
        "body{font:15px system-ui;background:#f3f6fb;color:#14253d;margin:0}"
        "main{max-width:1320px;margin:auto;padding:32px}header{background:#12283f;color:white;padding:28px;border-radius:12px}"
        ".eyebrow{letter-spacing:.12em;font-size:12px;color:#a6dfe2}h1{font-size:28px;margin:12px 0}"
        ".cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px;margin:20px 0}"
        ".card{background:white;border:1px solid #d6e0ec;border-top:4px solid #007f86;padding:18px;border-radius:8px}"
        ".card span{display:block;color:#56677b;font-size:12px}.card strong{font-size:25px;display:block;margin-top:8px}"
        "h2{font-size:20px;margin-top:30px}.table-wrap{overflow:auto;background:white;border-radius:8px}"
        "table{border-collapse:collapse;width:100%;font-size:12px}th,td{border-bottom:1px solid #dce4ee;padding:10px;text-align:left}"
        "th{background:#e9eff7}p{line-height:1.6}.notice{border-left:4px solid #cc8500;padding:12px;background:#fff4d9}"
        "</style><main><header><div class='eyebrow'>FINANCIAL CONTROL / SYNTHETIC REVIEW</div><h1>"
        + escape(title) + "</h1><strong>" + state + "</strong></header><div class='cards'>" + card_html
        + "</div><p class='notice'>A complete totals bridge is not proof that all differences are resolved. "
        "Pending metrics refer to keyed detail; unassigned amounts are separate. All values and identifiers are fictitious.</p>"
        "<h2>Decision summary</h2>" + table(summary)
        + "<h2>Source totals → detail → unassigned</h2><p>Bridge monetary values below are integer cents; displayed detail uses currency units. "
        "Exact bridge: actual − expected = keyed detail + unassigned.</p>" + table(bridge)
        + "<h2>Review detail</h2>" + table(display_detail(result))
        + "<h2>Evidence allocations</h2><p>Allocation amounts remain integer cents.</p>" + table(result.allocations)
        + "<h2>Unassigned source records</h2>" + table(result.unassigned)
        + "<h2>Pipeline stage ledger</h2>" + table(pd.DataFrame(result.trace))
        + "<p>Line and amount evidence capacities are independent. Per-status distinct students are not additive across statuses.</p></main></html>"
    )


def export_review(result, directory, title):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    for name, frame in {
        "detail": result.detail, "allocations": result.allocations, "unassigned": result.unassigned,
        "summary": summarize_review(result), "trace": pd.DataFrame(result.trace)
    }.items():
        frame.to_csv(directory / f"{name}.csv", index=False)
    (directory / "kpis.json").write_text(json.dumps(result.kpis, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (directory / "report.html").write_text(render_html(result, title), encoding="utf-8")
