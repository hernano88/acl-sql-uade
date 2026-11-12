# Interview deep dive · decisions and tradeoffs

[Español](interview_deep_dive.es.md) · [Home](../README.md)

## 1. Start with the grain, not the merge syntax

All new controls select a period first, then compare student/program keys. Original enrollment
and billing summaries used student-only grain. The public change prevents cross-program
compensation but cannot detect substitution of two subjects inside one key.
To claim exact matching, add subject/concept/installment lineage and validate those relations.

The source ID contract catches repeated ingestion; the summarized one_to_one join catches a
different failure: a broken grain on either side. Scholarship configuration has its own
many_to_one relationship, so a duplicate program rule must fail before multiplying the base.

Code: [contracts](../src/financial_controls/contracts.py),
[control adapters](../src/financial_controls/controls.py),
[reconciliation](../src/financial_controls/reconciliation.py).

## 2. Money needs a declared policy

A decimal source value 1.005 becomes 101 cents using half-up. Signed event cents are then
summed. Scholarship percentages round once per student/program, not once per source event.
Those decisions affect totals and are explicit public policies, not assumed institutional ones.
A one-cent tolerance changes status, not the stored delta. Net and absolute metrics retain it.

Code: [money](../src/financial_controls/money.py).
Tests include invalid/non-finite values, negative amounts, rounding boundaries and count-only discrepancies.

## 3. Explanation is not deletion

The engine preserves original delta, signed justified amount and signed residual.
Evidence is direction-aware, unique by ID and capped at the outstanding difference.
Raw DE MÁS/DE MENOS remains visible after review status becomes JUSTIFICADO.
A case that closes amount but not count stays pending.

Independent capacity limits do not prove invoice-line attribution. Two semantically overlapping
evidence rows with different IDs would need additional lineage rules. The fixtures deliberately
use independent evidence; the limitation is documented rather than hidden.

## 4. Prove conservation separately from correctness

Billing fixture: 890.00 − 930.00 = −40.00; +190.00 explained excesses and −230.00 unresolved
shortages reconstruct that difference. The bridge reconciles while the control remains open.

Scholarship fixture: 65.00 − 45.00 = 20.00; keyed deltas 17.00 + unassigned 3.00 explain the total.
A left join from theory alone could lose applied-only benefits. Distributing the missing-program
benefit across both programs could duplicate it. The outer join and separate ledger avoid both.

## 5. Trace stages without logging records

The result trace shows scoped input counts/exclusions, aggregate grains, join cardinality,
classification, evidence allocation and the totals check. The same events can be logged with
--verbose. Neither log nor trace contains student IDs, connection values or source records.
The trace documents a run; it is not a production scheduler or immutable audit-log service.

Code: [trace](../src/financial_controls/trace.py), [reporting](../src/financial_controls/reporting.py).

## 6. Integration and security boundary

The [Oracle example](../examples/oracle_connection.py) binds period values, keeps credentials
external, avoids URL interpolation and disposes the engine. It is inert on import.
Offline tests cannot prove database object permissions, snapshot consistency, performance or
Oracle/Pandas type mapping. Those need an authorized isolated integration environment.

The public artifacts are authored synthetic data, not hashed production rows.
The text scanner is a guardrail, not certification of all possible secrets or historical binaries.

## Suggested live interview

1. Read the [billing notebook](../notebooks/02_assigned_vs_billed.ipynb).
2. Show why equal total line counts do not close individual cases.
3. Trace one DE MÁS through its allocation and one DE MENOS into pending.
4. Run the duplicate-rule and partial-justification tests.
5. Explain the unassigned scholarship bridge and remaining business decisions.

See [test suite](../tests/test_financial_controls.py), [control matrix](control_matrix.md) and
[limits](limitations.md). Avoid claiming performance or business-impact metrics that these
artifacts do not measure.
