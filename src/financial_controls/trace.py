"""Small metadata-only stage ledger; no source records or connection data are logged."""
import logging

LOGGER = logging.getLogger("financial_controls")


def record(trace, stage, rows, check):
    event = {"stage": stage, "rows": int(rows), "check": check}
    trace.append(event)
    LOGGER.info("stage=%s rows=%d check=%s", stage, int(rows), check)


def scoped(trace, name, original, selected):
    record(trace, "scope." + name, len(selected),
           f"validated_keys_and_row_ids; excluded_rows={len(original) - len(selected)}")
