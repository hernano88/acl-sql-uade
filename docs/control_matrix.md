# Control matrix and independently expected fixture outcomes

| Control | Assertion | Evidence / action |
|---|---|---|
| ENR-01 | Assigned counts correspond to enrollment counts at composite grain | Outer-join both universes |
| ENR-02 | Missing lines can be explained by bounded evidence | Cash then non-chargeable capacity |
| ENR-03 | Extra assigned lines have explicit explanation | Prior-period capacity; retain residual |
| BILL-01 | Assigned and billed amounts AND counts agree | Compare both dimensions independently |
| BILL-02 | Manual adjustments do not overjustify | Bounded line/cent allocations |
| SCH-01 | Eligibility follows a unique configured rule | many-to-one rule join; no silent default |
| SCH-02 | Applied and theoretical benefits agree | Outer join, original signed difference |
| SCH-03 | Missing program cannot duplicate a benefit | Separate unassigned ledger |
| ALL-01 | Source events are not accidentally duplicated | Unique event IDs before grouping |
| ALL-02 | Detail accounts for source totals | Mother = detail + unassigned |
| ALL-03 | Justifications preserve arithmetic | Original = justified + pending |
| ALL-04 | Opposite differences remain visible | Net AND absolute residuals |

Fixture period: 2030-09. Currency units below are fictitious.

| Result | Enrollment | Billing | Scholarship |
|---|---:|---:|---:|
| Expected lines | 10 | 9 | Not a scholarship measure |
| Actual lines | 9 | 9 | Not a scholarship measure |
| Expected amount | Not measured | 930.00 | 45.00 |
| Actual amount incl. unassigned | Not measured | 890.00 | 65.00 |
| Mother difference amount | Not measured | -40.00 | +20.00 |
| Keyed detail difference amount | Not measured | -40.00 | +17.00 |
| Unassigned amount | 0.00 | 0.00 | 3.00 |
| Pending keyed cases | 2 | 2 | 2 |
| Pending keyed net amount | Not measured | -230.00 | +12.00 |
| Pending keyed absolute amount | Not measured | 230.00 | 12.00 |

SYN-S001 has two programs. Its unassigned 3.00 benefit must never be added to both.
SYN-S005 has an applied benefit without a theoretical billed base and must appear right_only.
SYN-S003 and SYN-S006 illustrate missing billing; SYN-S004 and SYN-S007 have explicit
synthetic manual adjustments. Some cases are deliberately unresolved.
Expected results are asserted in tests rather than accepted solely because the engine produced them.
