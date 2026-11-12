# Data dictionary — three synthetic controls

All rows use invented SYN- identifiers. Dates and monetary amounts are fictitious.
CSV ingestion uses string types. Missing fields are not converted to zero globally.

| Field | Input / meaning | Contract |
|---|---|---|
| row_id | Source event / exception identifier | Nonblank, unique within each input file |
| student_ref | Fictitious student | Trimmed uppercase string; required |
| program_ref | Fictitious program | Required except applied scholarships without program |
| period | Billing scope | YYYY-MM; explicit run parameter |
| amount | Currency units | Finite decimal string; row rounded half-up to cents |
| chargeable | Enrollment is chargeable | Y/N; unknown rejected |
| prior_period | Assigned row explains prior-period excess | Y/N, synthetic |
| manual_adjustment | Billed row is explanatory adjustment | Y/N, synthetic |
| min_subjects | Scholarship eligibility count | Integer >= 1 |
| rate_bps | Scholarship rate in basis points | Integer 0..10000 |
| rule | Synthetic exception category | SYNTHETIC_ prefix |
| direction | Exception applies to excess or shortage | +1 or -1 |

| Fixture | Grain |
|---|---|
| enrollments.csv | One enrollment event |
| assigned.csv | One assigned billing line |
| billed.csv | One posted billing line |
| cash.csv | One synthetic cash justification unit |
| scholarships.csv | One applied benefit; program may be missing |
| scholarship_rules.csv | One program per period |
| scholarship_exceptions.csv | One independent synthetic evidence capacity |

## Result fields

`lines_expected / lines_actual`: aggregated source line counts.
`cents_expected / cents_actual`: integer-cent sums.
`difference_*`: actual minus expected, unchanged by justification.
`justified_*`: signed consumed evidence capacity.
`pending_*`: original minus justified.
`presence`: left_only / right_only / both from the outer join.
`raw_status`, `review_status`, `mixed_direction`: see business_rules.md.

The allocation ledger records composite key, unique evidence ID, synthetic rule, direction
and nonnegative capacities actually consumed. Unused capacity is not added to the difference.
The unassigned ledger preserves source rows that cannot join safely.
Scholarship detail additionally includes subjects, minimum, rate and billed base; actual-only
keys have missing theoretical metadata, intentionally not fabricated zeros.

KPI fields distinguish mother/detail differences, unallocated and explicitly unassigned
amounts, keyed pending net/absolute values, case counts and distinct pending students.
Pending metrics refer to keyed detail; unassigned rows/amounts are reported separately.
All files use one fictitious currency. Multi-currency conversion is out of scope.

The [earlier example dictionary](DATA_DICTIONARY.md) is retained for the legacy public fixtures.
