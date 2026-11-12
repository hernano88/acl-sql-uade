# Limits and next steps

This is a portfolio demonstration of control design, not a certified accounting system.

- Static review of professional notebooks supports technical patterns, not verified performance
  or business-impact metrics. No production query was executed for this project.
- Public composite keys, strict null contracts, Decimal ingestion, allocation ledgers and
  fresh-kernel tests are engineering improvements, not retroactive claims about the originals.
- Aggregate counts/amounts can conceal substitutions inside the same key. Exact subject,
  concept, invoice and installment matching would need additional contracts.
- Evidence allocations cap lines and cents independently. They do not prove exact transaction
  attribution. Fixture evidence rows are independent by construction; semantic overlap across
  different evidence IDs needs additional business lineage rules.
- The public model uses one currency and one explicit period. Row-level half-up rounding and
  one-cent tolerance are documented demo policies, not institutional accounting advice.
- Missing-program benefits are reported, not automatically allocated.
- No production scheduling, historical Oracle persistence, performance benchmark, live database
  integration, access-control framework or measured financial savings is claimed.
- CSV is the portable review export. The private workflow's Excel output is evidenced, but the
  new package does not require Excel or reproduce private workbook layouts.
- Dependency ranges are bounded, not a fully locked cross-platform environment. CI covers
  Python 3.11/3.12; only the locally reported runtime is actually tested during implementation.
- Historical examples and images are archived outside the current walkthrough. New notebook
  execution and text scanning do not independently validate their historical business claims.

Next: reviewer agreement on synthetic semantics; exact line-matching prototype; integration
tests against an isolated Oracle sandbox; dependency lock and broader platform checks if needed.
Production adoption would require authorized data contracts and business validation separately.
