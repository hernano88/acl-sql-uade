"""Escaped HTML and portable CSV review outputs; no network or database writes."""
from html import escape
from pathlib import Path
import json
from .money import format_cents


def render_html(result, title):
    metrics = []
    for key, value in result.kpis.items():
        shown = format_cents(value) if key.endswith("_cents") else str(value)
        metrics.append(f"<tr><th>{escape(key)}</th><td>{escape(shown)}</td></tr>")
    return (
        "<!doctype html><html lang='en'><meta charset='utf-8'>"
        "<title>" + escape(title) + "</title>"
        "<style>body{font:15px system-ui;margin:2rem;color:#17243b}"
        "table{border-collapse:collapse;margin:1rem 0}th,td{border:1px solid #ccd5e0;"
        "padding:.4rem;text-align:left}th{background:#edf2f8}</style>"
        "<h1>" + escape(title) + "</h1><p>PUBLIC SYNTHETIC DATA ONLY. "
        "A reconciled totals bridge does not mean that all exceptions are resolved. "
        "Detail monetary columns are integer cents.</p>"
        "<h2>Independent totals and review metrics</h2><table>" + "".join(metrics) + "</table>"
        "<h2>Keyed detail</h2>" + result.detail.to_html(index=False, escape=True)
        + "<h2>Justification allocations</h2>" + result.allocations.to_html(index=False, escape=True)
        + "<h2>Unassigned source records</h2>" + result.unassigned.to_html(index=False, escape=True)
        + "</html>"
    )


def export_review(result, directory, title):
    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    result.detail.to_csv(directory / "detail.csv", index=False)
    result.allocations.to_csv(directory / "allocations.csv", index=False)
    result.unassigned.to_csv(directory / "unassigned.csv", index=False)
    (directory / "kpis.json").write_text(json.dumps(result.kpis, indent=2, ensure_ascii=False) + "\n",
                                         encoding="utf-8")
    (directory / "report.html").write_text(render_html(result, title), encoding="utf-8")
