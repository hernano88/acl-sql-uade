# Financial controls with Python, Pandas, Jupyter and Oracle SQL

[Español](README.es.md)

Three reproducible, **fully synthetic** case studies of financial control modernization.
The work builds on control knowledge originally implemented with **ACL Analytics and Oracle SQL**.
Python and Jupyter are the focus of this portfolio; ACL remains available as historical context.

| Case | Question | Measures | Public key |
|---|---|---|---|
| [01 — Enrollment vs assigned billing](notebooks/01_enrollment_vs_assigned.ipynb) | Do assigned billing lines match academic enrollment? | Line counts | Student + program |
| [02 — Assigned vs billed](notebooks/02_assigned_vs_billed.ipynb) | Were assigned concepts actually billed? | Lines + cents | Student + program |
| [03 — Expected vs applied scholarship](notebooks/03_expected_vs_applied_scholarship.ipynb) | Does the applied benefit match synthetic eligibility? | Cents; enrollment counts as inputs | Student + program |

The examples deliberately contain unresolved exceptions. A successful **totals bridge** means
that source totals are accounted for; it does not mean that every transaction is correct.

## Run locally without Oracle

Python 3.11+; commands run from the repository root:

```bash
python -m venv .venv
# Activate .venv (Windows PowerShell: .venv/Scripts/Activate.ps1)
# macOS/Linux: source .venv/bin/activate
python -m pip install -e ".[dev,notebooks]"
python -m pytest -q
python -m financial_controls.demo --period 2030-09 --output artifacts
python scripts/run_notebooks.py
python scripts/scan_public.py
```

Open a notebook with JupyterLab, or review each generated `artifacts/<case>/report.html`.
Every case exports detail, justification allocations, unassigned rows and KPI JSON.
Monetary detail fields ending in `cents` are integers, not currency-unit floats.

## Evidence from real work vs public synthetic demonstration

| Evidence from the reviewed professional notebooks | Public demonstration / engineering improvement |
|---|---|
| Oracle extraction into Pandas, grouping and merges | Offline CSV fixtures; optional, inert Oracle connection example |
| Enrollment and billing quantity comparisons | Composite keys in all three public controls; the first two originals grouped by student |
| Billing reconciliation of lines and amounts | Shared bidirectional engine with integer-cent contracts |
| Scholarship theory, applied amount, composite key and merge validation | Configurable **synthetic** minimum and rate; missing configuration fails |
| Business justifications, pending cases and HTML reports; one Excel export | Explicit capped allocations, portable CSV/HTML outputs |
| Mother/detail total reconciliation | Independent totals, unassigned bridge, net and absolute residuals |
| Selected `one_to_one` / `many_to_one` checks in scholarship | Declared cardinality and source-row uniqueness contracts throughout |

The originals are private and are neither distributed nor imported. The audit observed code
and saved outputs; it did not rerun production processing or independently certify operational
accuracy, cadence, ownership, scale or impact. This repository does not claim a completed
migration, scheduled deployment, production history tables, leadership seniority or measured savings.
Previously described coverage/volume figures are not used as validated outcomes of these three cases.

**All public rules, identifiers, amounts, source names and dates in the new cases are fictitious.**
The synthetic scholarship uses a minimum of two subjects and a 10% rate solely for demonstration.
Those values and allowance amounts do not disclose institutional policy.
See [business rules](docs/business_rules.md) and [limitations](docs/limitations.md).

## Control decisions worth discussing in an interview

- Aggregate at an explicit grain. Equal student totals can hide differences between programs.
- Normalize strings without converting identifiers to numbers; reject missing keys.
- Preserve both universes with an outer join; validate one-to-one summarized joins.
- Read decimal strings, round half-up to cents and perform arithmetic with integers.
- Keep `raw_status` (`OK`, `DE MÁS`, `DE MENOS`) separate from review status.
- Cap each justification, retain the original difference and expose partially explained cases.
- Keep scholarships without a program unassigned; never replicate them across a student's programs.
- Compare pre-join totals with keyed detail plus explicitly unassigned amounts.
- Report net and absolute residuals; do not hide offsetting exceptions.
- Parameterize periods rather than relying on the execution date.

## Architecture and review material

```mermaid
flowchart LR
    A[Synthetic CSV / optional Oracle contract] --> B[Validation and normalization]
    B --> C[Case-specific eligibility and aggregation]
    C --> D[Shared full outer reconciliation]
    D --> E[Capped evidence allocations]
    E --> F[Detail + pending + unassigned]
    F --> G[Independent totals bridge]
    G --> H[HTML / CSV / notebook review]
```

- [Architecture](docs/architecture.md)
- [Data dictionary](docs/synthetic_data_dictionary.md)
- [Control matrix and known results](docs/control_matrix.md)
- [Business rules and allocation assumptions](docs/business_rules.md)
- [Security boundary](docs/security.md)
- [Limitations and roadmap](docs/limitations.md)
- [Interview and LinkedIn wording](docs/professional_summary.md)

`src/financial_controls/` contains the shared engine and three small control adapters.
`tests/` covers both the new cases and the earlier public reconciliation example.
CI runs tests, executes all three notebooks in fresh kernels, generates review reports and scans
public text. It does not connect to Oracle.

## Oracle SQL and ACL legacy

[SQL examples](sql/) and [ACL example](acl/financial_control_coverage.acl) remain available.
[Composite-grain Oracle SQL](sql/05_synthetic_composite_scope.sql) is a standalone synthetic
query; Oracle execution is optional and has not been validated by the Python test suite.

The [connection template](python_jupyter/oracle_connection.example.py) reads environment variables
only inside an explicitly called function. Importing it does not connect. It uses fictitious view
names and bound period parameters; no real infrastructure is required for the portfolio.

The [earlier generic notebook](python_jupyter/notebooks/01_synthetic_billing_reconciliation.ipynb),
[module](python_jupyter/src/control_reconciliation.py), fixtures and tests are preserved.
Its original synthetic coverage example remains an illustration, not evidence of current
production coverage. New features should use the shared package above.
