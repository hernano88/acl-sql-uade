# Validation and review procedure

The local implementation is checked with:

```bash
python -m pytest -q
python -m financial_controls.demo --period 2030-09 --output artifacts --verbose
python scripts/run_notebooks.py
python scripts/build_portfolio_assets.py
python scripts/check_links.py
python scripts/scan_public.py
git diff --check
```

The suite includes independent fixture expectations, duplicates in events and rule configuration,
critical nulls, decimal boundaries, non-finite amounts, count-only differences, conflicting
directions, partial/wrong-direction evidence, signed reversals, empty scopes and invalid periods,
applied-only benefits, missing-program records, net/absolute metrics, conservation and trace.

The two earlier example tests remain active against the archived module and fixtures.
New tests assert that stage order is coherent, logs do not contain student identifiers,
summary totals agree with detail and trace exports exist.

Each public notebook is executed from a fresh kernel and includes assertions.
The runner writes artifacts by default; --publish refreshes the three public notebooks with
scrubbed metadata and synthetic outputs. Review fixture prefixes and scanner results before publishing.

The asset script derives diagrams, result snapshots and sample exports from the control results.
The link checker inspects current Markdown, notebook narratives and image references.
Text scanning covers current source and published outputs; it does not certify images,
remote history or all possible secret formats.

The workflow runs the same checks. Its run status must be reported separately from local
validation. Oracle is never used by these checks; no database integration result is claimed.
