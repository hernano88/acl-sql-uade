-- Expected-versus-actual reconciliation by billing concept.

WITH reconciled_lines AS (
    SELECT
        l.concept_code,
        c.concept_name,
        c.strong_control_flag,
        l.expected_amount,
        l.billed_amount,
        l.billed_amount - l.expected_amount AS amount_difference,
        NVL(r.control_status, 'PENDING') AS control_status
    FROM portfolio_billing_line l
    INNER JOIN portfolio_billing_concept c
        ON c.concept_code = l.concept_code
    LEFT JOIN portfolio_control_result r
        ON r.line_id = l.line_id
)
SELECT
    concept_code,
    concept_name,
    strong_control_flag,
    control_status,
    COUNT(*) AS line_count,
    SUM(expected_amount) AS total_expected,
    SUM(billed_amount) AS total_billed,
    SUM(amount_difference) AS total_difference
FROM reconciled_lines
GROUP BY
    concept_code,
    concept_name,
    strong_control_flag,
    control_status
ORDER BY concept_code;
