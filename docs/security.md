# Publication boundary

Only public repository assets and newly authored synthetic fixtures are inputs to this change.
The production notebooks, external configuration, exports and saved outputs are excluded.

New sources contain no institutional table/schema names, real student IDs, infrastructure
addresses, connection strings or production results. Oracle source names use portfolio_synthetic_
placeholders. The connection template has no import-time side effects and never prints a DSN
or password. Environment-variable names are configuration contracts, not secret values.

Before publication:
1. Run tests and execute the three synthetic notebooks.
2. Generate local review artifacts from synthetic CSVs.
3. Run scripts/scan_public.py (working-tree text patterns and synthetic identifier prefix checks).
4. Review git diff and file inventory, including notebook outputs.
5. Publish only the branch/PR; do not merge automatically.

The scanner prints categories and paths, never matched secret values. It is not proof of
absence of all secrets and does not inspect binary images, remote history or external
configuration. Existing legacy screenshots remain unchanged and are not re-certified by this
text scan. New illustrations and result snapshots are generated SVGs from synthetic data only. No new screenshot of a production
system is included. Generated notebooks contain synthetic outputs only; canonical notebooks
include executed synthetic outputs and scrubbed metadata, without local paths.

Do not replace real IDs with hashes and call the data synthetic. Public scenarios are authored
from scratch. If a real credential is ever found in history, stop publication and address
revocation and history cleanup separately.
