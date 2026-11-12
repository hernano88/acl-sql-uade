"""Deterministic offline entry point for the three public cases."""
import argparse
import logging
from pathlib import Path
import pandas as pd
from .controls import enrollment_control, billing_control, scholarship_control
from .reporting import export_review

DEMO_PERIOD = "2030-09"


def load_inputs(root):
    directory = Path(root) / "data" / "synthetic"
    return {p.stem: pd.read_csv(p, dtype="string", keep_default_na=False)
            for p in sorted(directory.glob("*.csv"))}


def run_cases(root, period=DEMO_PERIOD):
    data = load_inputs(root)
    return {
        "01_enrollment": enrollment_control(data["enrollments"], data["assigned"], data["cash"],
                                             period=period),
        "02_billing": billing_control(data["assigned"], data["billed"], period=period),
        "03_scholarship": scholarship_control(
            data["enrollments"], data["billed"], data["scholarships"],
            data["scholarship_rules"], data["scholarship_exceptions"], period=period
        ),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--period", default=DEMO_PERIOD)
    parser.add_argument("--output", type=Path, default=Path("artifacts"))
    parser.add_argument('--verbose', action='store_true', help='Log stage metadata only')
    args = parser.parse_args()
    if args.verbose:
        logging.basicConfig(level=logging.INFO, format='%(name)s %(message)s')
    for name, result in run_cases(args.root, args.period).items():
        export_review(result, args.output / name, f"{name} | {args.period} | synthetic")
        print(name, "pending cases:", result.kpis["pending_cases"],
              "unassigned rows:", result.kpis["unassigned_rows"])


if __name__ == "__main__":
    main()
