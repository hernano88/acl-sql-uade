"""Generate public diagrams, result snapshots and sample exports from synthetic fixtures."""
from pathlib import Path
from html import escape
from financial_controls.demo import run_cases, DEMO_PERIOD
from financial_controls.reporting import export_review
from financial_controls.money import format_cents

ROOT = Path(__file__).resolve().parents[1]
NAVY, TEAL, MUTED = "#112a43", "#087e87", "#52677d"


def text(x, y, value, size=16, fill=NAVY, weight="400"):
    return f'<text x="{x}" y="{y}" fill="{fill}" font-size="{size}" font-weight="{weight}">{escape(str(value))}</text>'


def rect(x, y, width, height, fill="white", stroke="#d5e1ee"):
    return f'<rect x="{x}" y="{y}" width="{width}" height="{height}" rx="12" fill="{fill}" stroke="{stroke}"/>'


def save(name, height, pieces, title):
    directory = ROOT / "docs" / "images"
    directory.mkdir(parents=True, exist_ok=True)
    body = "".join(pieces)
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="1280" height="{height}" '
        f'viewBox="0 0 1280 {height}" role="img" aria-labelledby="title">'
        f'<title id="title">{escape(title)}</title>'
        f'<rect width="1280" height="{height}" fill="#f3f7fc"/>'
        f'<g font-family="Arial, Helvetica, sans-serif">{body}</g></svg>\n'
    )
    (directory / name).write_text(svg, encoding="utf-8")


def architecture():
    p = [text(36, 48, "FROM SOURCE DATA TO REVIEWABLE FINANCIAL CONTROLS", 25, weight="700"),
         text(36, 80, "Offline fixtures are executable. Oracle is a safe optional extraction contract.", 17, MUTED)]
    labels = [
        ("SOURCE", ["Synthetic CSV fixtures", "Optional Oracle SQL", "External configuration"]),
        ("CONTRACT", ["Period + source row ID", "Student / program keys", "Critical null checks"]),
        ("PANDAS", ["Normalize and scope", "Counts + integer cents", "Eligibility by program"]),
        ("CONTROL ENGINE", ["Validated outer joins", "Bounded evidence", "Original + residual"]),
        ("REVIEW", ["Independent totals bridge", "HTML / CSV / JSON", "Summary + stage ledger"]),
    ]
    for i, (label, lines) in enumerate(labels):
        x = 36 + i * 246
        p += [rect(x, 124, 224, 180), text(x + 18, 157, label, 16, TEAL, "700")]
        for j, line in enumerate(lines):
            p.append(text(x + 18, 197 + j * 29, line, 15))
        if i < 4:
            p += [f'<path d="M{x+226} 215 H{x+241}" stroke="{TEAL}" stroke-width="3"/>',
                  f'<path d="M{x+235} 209 L{x+242} 215 L{x+235} 221" fill="none" stroke="{TEAL}" stroke-width="3"/>']
    p += [rect(36, 336, 1208, 55, "#e5f2f2"),
          text(56, 370, "SCOPE  →  NORMALIZE  →  AGGREGATE  →  COMPARE  →  EXPLAIN  →  RECONCILE  →  REVIEW", 18, TEAL, "700"),
          text(36, 422, "No production connection, query, identifier, result or screenshot is included.", 16, MUTED)]
    save("architecture.svg", 450, p, "End-to-end financial control architecture")


def overview(cases):
    titles = ["01  ENROLLMENT", "02  BILLING", "03  SCHOLARSHIP"]
    subtitles = ["Academic activity → assigned billing", "Assigned concepts → posted movements", "Theoretical benefit → applied benefit"]
    p = [text(36, 45, "THREE CONTROLS. ONE SHARED PYTHON ENGINE.", 27, weight="700"),
         text(36, 77, "Synthetic result overview · period " + DEMO_PERIOD + " · no production metrics", 17, MUTED)]
    for i, result in enumerate(cases.values()):
        x = 36 + i * 412
        k = result.kpis
        p += [rect(x, 110, 384, 270), text(x+22, 148, titles[i], 20, TEAL, "700"),
              text(x+22, 179, subtitles[i], 16)]
        primary = f'{k["expected_lines"]} → {k["actual_lines"]} lines' if i == 0 else (
            f'{format_cents(k["expected_cents"])} → {format_cents(k["actual_cents"])}'
        )
        p += [text(x+22, 230, primary, 29, weight="700"),
              text(x+22, 264, "expected → actual", 14, MUTED),
              text(x+22, 308, f'{k["pending_cases"]} pending composite keys', 19, weight="700")]
        foot = ["Pending net 0; absolute 2 lines", "Pending shortages 230.00; net delta −40.00",
                "3.00 unassigned; full bridge reconciles"][i]
        p.append(text(x+22, 343, foot, 15, MUTED))
    p += [text(36, 420, "Original difference + evidence allocation + pending residual + independent totals", 20, weight="700"),
          text(36, 452, "Executed notebooks • strict keys • validated joins • integer cents • HTML / CSV review", 17, MUTED)]
    save("control-overview.svg", 480, p, "Three synthetic financial control case studies")


def snapshot(name, result):
    titles = {"01_enrollment": "ENROLLMENT VS ASSIGNED BILLING",
              "02_billing": "ASSIGNED VS BILLED MOVEMENTS",
              "03_scholarship": "EXPECTED VS APPLIED SCHOLARSHIP"}
    money = name != "01_enrollment"
    measure = "cents" if money else "lines"
    show = format_cents if money else str
    rows = result.detail.to_dict("records")
    h = 240 + len(rows) * 48
    p = [text(32, 42, titles[name], 27, weight="700"),
         text(32, 75, "Generated from synthetic fixtures · " + DEMO_PERIOD + " · amounts in fictitious currency units", 16, MUTED),
         rect(32, 99, 1216, 52, "#e5f2f2"),
         text(48, 132, f'Pending keys: {result.kpis["pending_cases"]}     |     Unassigned amount: {format_cents(result.kpis["unassigned_cents"])}     |     Totals bridge: complete', 19, TEAL, "700")]
    headers = [(46,"STUDENT / PROGRAM"),(330,"EXPECTED"),(474,"ACTUAL"),(608,"DELTA"),(750,"RAW STATUS"),(923,"REVIEW")]
    for x,label in headers:
        p.append(text(x,184,label,13,MUTED,"700"))
    for i,row in enumerate(rows):
        y = 202+i*48
        p.append(rect(32,y,1216,43,"white"))
        values = [
            (46, row["student_ref"]+" / "+row["program_ref"]),
            (330, show(int(row[f"{measure}_expected"]))),
            (474, show(int(row[f"{measure}_actual"]))),
            (608, show(int(row[f"difference_{measure}"]))),
            (750, row["raw_status"]), (923,row["review_status"])
        ]
        color = "#a64f05" if row["review_status"] == "PENDIENTE" else TEAL
        for x,value in values:
            p.append(text(x,y+28,value,16,color if x>=750 else NAVY,"700" if x>=750 else "400"))
    p.append(text(34,h-12,"A complete bridge does not mean all cases are resolved. Unassigned values are separate from keyed pending.",15,MUTED))
    save(name+".svg",h,p,titles[name])


def main():
    cases = run_cases(ROOT)
    architecture()
    overview(cases)
    for name, result in cases.items():
        snapshot(name, result)
        export_review(result, ROOT / "docs" / "outputs" / name, name + " | " + DEMO_PERIOD + " | SYNTHETIC")
    (ROOT / "docs" / "outputs" / "README.md").write_text(
        "# Generated synthetic review samples\n\nThese files are generated by "
        "scripts/build_portfolio_assets.py from data/synthetic.\n"
        "Open report.html locally; GitHub displays HTML source. "
        "CSV money is integer cents. No production result is included.\n", encoding="utf-8")
    print("Generated 5 SVG diagrams/snapshots and 3 complete review-export sets")


if __name__ == "__main__":
    main()
