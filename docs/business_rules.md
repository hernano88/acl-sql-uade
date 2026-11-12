# Public synthetic rules

These are fictitious teaching rules. No institutional catalog, code or confidential parameter
is copied. The patterns (count comparison, theoretical benefit, capped justifications) reflect
the reviewed work; the constants and evidence model below are synthetic.

## 01 Enrollment vs assigned

Each enrollment and assigned row counts as one line. Key: student + program + selected period
(period is scoped before joining). All enrollments count initially. Missing assigned lines
may be explained by cash events first, then explicitly non-chargeable enrollments.
Extra assigned lines may be explained by assigned rows marked prior-period.
Capacity is consumed sequentially and never exceeds the remaining difference.
Chargeability must be Y/N: null is a data error, not evidence of a free subject.

The two original non-scholarship controls grouped by student. The public composite grain is
a deliberate improvement; this does not assert it was implemented throughout the originals.

## 02 Assigned vs billed

Every assigned and billed row contributes one line and its signed amount. Extra billed
amounts/lines may be explained by rows explicitly marked as manual adjustments.
This flag is synthetic; it substitutes for private source-specific academic metadata.
Missing billed amounts/lines have no automatic justification in this case.
Signed accounting reversals remain signed. Negative adjustment capacities require review.

Line and amount capacities are independently capped. A partial justification remains pending;
this model does not establish exact source-line correspondence or uniquely attribute a cent
to an invoice. Rows with opposing line/amount directions retain a mixed-direction flag.

## 03 Theoretical vs applied scholarship

A fictional student/program qualifies at two enrollments. The benefit is 10% (1000 basis
points) of selected billed amounts for that key. The canonical applied amount is a positive
benefit; negatives are rejected for explicit review instead of being silently converted with abs().
Missing eligibility configuration fails; no default minimum is assumed.
A benefit applied without a theoretical key is preserved by the outer join.

Two explicitly synthetic evidence records demonstrate a non-chargeable allowance and a
special benefit, with fixed capacities and directions. They do not reproduce institutional
exception amounts, codes or broad student-membership overrides.
Missing-program benefits stay in a separate unassigned ledger. No automatic distribution
across a student's programs is attempted.

## Statuses

`raw_status`: DE MÁS for actual greater than expected, DE MENOS for actual lower than expected,
OK within one cent and with no line difference. Amount determines the label when line and
amount directions conflict; `mixed_direction` flags the conflict.
`review_status`: OK (no material residual and no allocation), JUSTIFICADO (allocation closes
both dimensions), PENDIENTE (a dimension remains unresolved).
Raw deltas and sub-tolerance residuals are always preserved in detail and metrics.
