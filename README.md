# Financial Billing Reconciliation with ACL Analytics and Oracle SQL

[English](README.md) | [Español](README.es.md)

A professional data-control case study based on automated billing reconciliation work. The solution combines Oracle SQL for extracting and shaping operational data, ACL Analytics for repeatable control rules, and Excel outputs for business review and exception management.

All public code, data, identifiers, and screenshots are synthetic or sanitized. Production scripts, connection details, student information, and internal database objects are intentionally excluded.

## Business problem

High-volume billing combines enrollment, tuition, scholarships, discounts, cancellations, and special adjustments. These inputs can disagree across operational reports and database sources. Manual comparison is slow, difficult to repeat, and likely to miss low-frequency exceptions.

The control framework was designed to:

- compare expected and actual billing;
- reconcile enrollment and financial movements;
- apply business rules consistently;
- classify explainable differences;
- isolate unresolved exceptions before collection activities;
- measure how much financial value is protected by strong controls.

## Implemented workflow

```mermaid
flowchart LR
    A["Oracle operational sources"] --> B["Oracle SQL extraction"]
    B --> C["ACL normalization and joins"]
    C --> D["Business validation rules"]
    D --> E["Expected vs. actual reconciliation"]
    E --> F["Classified differences"]
    F --> G["Excel control report"]
    G --> H["Manual review of exceptions"]
```

Oracle SQL and ACL have different responsibilities: SQL builds the required data scope close to the source, while ACL standardizes fields, combines extracts, evaluates business rules, summarizes results, and exports the control report.

## Main KPI: monthly financial control coverage

The approximately **98%** result is a monthly financial-coverage metric, not prediction accuracy and not a claim that 98% of invoices are error-free.

```text
financial control coverage =
    billed amount covered by strong controls
    -----------------------------------------  x 100
                total billed amount
```

The synthetic monthly example included in this repository uses a total billed amount of 100,000 units. Concepts covered by strong automated controls account for 98,000 units, producing 98% financial control coverage for that billing period. The remaining 2% represents lower-volume or exceptional concepts routed to manual review.

![Synthetic example of 98 percent financial control coverage](docs/images/financial-control-coverage.png)

## Control layers

### 1. Oracle SQL extraction

Embedded Oracle SQL queries select the relevant billing period and combine enrollment, billing-line, concept, and control-result data. The representative public queries demonstrate:

- multi-table `INNER JOIN` and `LEFT JOIN` operations;
- common table expressions;
- date filtering and normalization;
- null handling with `NVL`;
- aggregation by concept and control status;
- reconciliation of expected and billed amounts.

```sql
SELECT
    l.account_ref,
    l.concept_code,
    l.expected_amount,
    l.billed_amount,
    NVL(r.control_status, 'PENDING') AS control_status
FROM portfolio_billing_line l
JOIN portfolio_billing_concept c
  ON c.concept_code = l.concept_code
LEFT JOIN portfolio_control_result r
  ON r.line_id = l.line_id;
```

![Synthetic example of multi-table SQL reconciliation logic](pictures/sql2.PNG)

### 2. ACL Analytics control logic

The operational controls use ACL scripts to:

- standardize account, date, and amount fields;
- create calculated differences and classification fields;
- build indexes and intermediate tables;
- join pre-billing and post-billing results;
- summarize controlled amounts and exceptions;
- delete temporary artifacts before reruns;
- export final control workbooks.

The public [`acl/financial_control_coverage.acl`](acl/financial_control_coverage.acl) file is a small representative example. It preserves the control pattern without exposing production code or connections.

### 3. Reconciliation and exception classification

Typical rules classify cases such as:

- enrolled but not billed;
- billed without a matching enrollment;
- billed before or after the expected period;
- cash or manual adjustments;
- scholarships or discounts outside their effective range;
- theoretical versus applied discount differences;
- low-volume cases requiring manual review.

![Synthetic expected-versus-actual billing control](pictures/check_masiva.PNG)

## Representative repository contents

```text
.
|-- acl/
|   `-- financial_control_coverage.acl
|-- data/
|   `-- synthetic_billing_control.csv
|-- docs/
|   |-- DATA_DICTIONARY.md
|   `-- images/
|       |-- financial-control-coverage.png
|       `-- financial-control-coverage.svg
|-- pictures/
|   `-- sanitized screenshots
|-- sql/
|   |-- 00_create_synthetic_tables.sql
|   |-- 01_extract_control_scope.sql
|   |-- 02_reconcile_expected_actual.sql
|   |-- 03_financial_control_coverage.sql
|   `-- 04_data_quality_checks.sql
|-- README.md
`-- README.es.md
```

## Demonstrated results

- Approximately **98% of monthly billed financial value** covered by strong controls for the defined scope.
- The most data-intensive controls processed datasets reaching approximately **5 GB** using ACL and Oracle-backed sources; this was a demonstrated maximum scale, not the standard size of every control.
- Repeatable classification of differences before downstream collection activities.
- Manual analysis focused on a smaller exception population instead of the complete billing universe.
- Reusable monthly and academic-period controls with reduced maintenance.

## Reproducing the synthetic example

1. Run the scripts under `sql/` in numerical order in an Oracle development environment.
2. Confirm that `03_financial_control_coverage.sql` returns 98% for the included data.
3. Review the same input in `data/synthetic_billing_control.csv`.
4. If ACL Analytics is available, adapt the representative script to an imported table with the same fields.

The SQL example is self-contained and uses only synthetic portfolio tables. ACL Analytics is commercial software, so the ACL script is provided as a readable implementation pattern rather than an automated CI test.

## Confidentiality and security

- No real student, customer, or employee data is included.
- No production table names, server names, DSNs, emails, passwords, or connection strings are included.
- Monetary values and identifiers are synthetic.
- Public scripts reproduce the technical pattern, not the production implementation.
- Screenshots are retained only when they contain sanitized or fictitious information.

## Professional summary

> I developed automated billing controls using ACL Analytics and Oracle SQL. SQL extracted and combined enrollment, billing, scholarship, discount, and adjustment data, while ACL standardized fields, applied business rules, reconciled expected versus actual amounts, and classified exceptions. Each month, the controls covered approximately 98% of total billed value within the defined scope, allowing manual review to focus on the remaining exceptional concepts. The most data-intensive controls processed datasets reaching approximately 5 GB and produced repeatable Excel control reports before collection activities.
