# Architecture

The package in `src/financial_controls` is the maintained implementation. The earlier
`python_jupyter/src/control_reconciliation.py` API remains unchanged for compatibility.

| Module | Responsibility |
|---|---|
| contracts | Required fields, periods, normalized composite keys, unique source IDs, explicit booleans |
| money | Decimal ingestion, half-up cents, integer-rate calculation, signed display |
| reconciliation | Aggregation, validated outer join, allocation ledger, statuses, independent totals |
| controls | Enrollment, billing and scholarship-specific universe/rule construction |
| reporting | Escaped HTML, CSV and JSON review exports |
| demo | Deterministic offline fixture loading and CLI |

All control functions are pure with respect to external systems: no connections, writes or
environment lookup. Only the CLI/report exporter writes local artifacts. Frames are copied
before mutation. No wall-clock period selection is used.

## Join contracts

Source event `row_id` values must be unique before aggregation. Duplicate events are errors,
not silently deduplicated. Student/program strings are trimmed and uppercased without numeric
conversion. Null/blank keys fail, except missing programs in applied scholarships, which are
routed to an unassigned ledger.

Aggregation produces one row per student/program. The comparison uses `outer` with
`validate="one_to_one"` and a presence indicator. Scholarship rules have one row per program
per selected period; the rule join uses `many_to_one`. Counts and enrichment joins use
`one_to_one`. There are no unchecked joins in the new package.

## Accounting identities

For each measure (lines and cents), with actual minus expected as the sign convention:

```text
mother difference = pre-join actual total - pre-join expected total
detail difference = sum(actual - expected at the composite key)
unallocated = mother difference - detail difference
mother difference = detail difference + explicitly unassigned source amounts
original difference = signed justified allocation + signed pending residual
```

`detail_reconciles` requires zero unallocated lines and at most the configured monetary
tolerance. `totals_bridge_reconciles` checks exact equality after including the unassigned
ledger. `control_clear` additionally requires no pending cases and no unassigned rows.
Unassigned rows are not silently labeled justified.

Evidence rows are globally unique within a control run and consumed once in stable priority
order. Their allocation is capped independently for lines and amount. This is an aggregate
explanatory model, not an exact invoice-line matching algorithm.

## Reproducibility

The fixture period is 2030-09. Other valid periods return empty scopes rather than reuse prior
state. Monetary inputs are decimal strings; each source row is rounded half-up to cents,
then summed. Rate amounts are rounded once per student/program. Default tolerance is one cent.
The policy is a public engineering choice, not a claim about institutional accounting policy.

CI tests Python 3.11 and 3.12, executes each new notebook in a fresh kernel and uploads review
artifacts. Oracle queries are examples, not integration-tested database adapters.
