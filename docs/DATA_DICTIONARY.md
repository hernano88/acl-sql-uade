# Synthetic data dictionary

The public example uses a deliberately small and fictitious dataset. It represents the minimum fields required to explain financial control coverage and exception handling.

| Field | Type | Description |
|---|---|---|
| `billing_period` | `YYYY-MM` | Synthetic billing month. |
| `account_ref` | string | Fictitious account identifier; it is not a student or customer ID. |
| `concept_code` | string | Generic billing concept. |
| `expected_amount` | decimal | Amount expected by the control logic. |
| `billed_amount` | decimal | Amount present in the synthetic billing result. |
| `strong_control_flag` | `Y` / `N` | Indicates whether the concept is covered by a strong automated control. |
| `control_status` | string | Reconciled, justified, or manual-review result. |
| `exception_reason` | string | Generic explanation when a difference or exception exists. |

## Coverage calculation

Only `billed_amount` is used to calculate financial control coverage:

```text
controlled_billed_amount =
    sum(abs(billed_amount)) where strong_control_flag = 'Y'

total_billed_amount =
    sum(abs(billed_amount)) for the complete defined monthly scope

financial_control_coverage_pct =
    controlled_billed_amount / total_billed_amount * 100
```

The use of absolute values makes the denominator explicit if a future synthetic example includes credit notes or negative adjustments. The current sample contains positive amounts only and returns exactly 98%.

## Confidentiality boundary

The field names are generic and do not reproduce a production schema. Production identifiers, institution-specific concept codes, connection parameters, and personal attributes are excluded.
