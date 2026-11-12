-- Compact exception report for the synthetic control tables.

SELECT 'MISSING_CONTROL_RESULT' AS issue_type, COUNT(*) AS issue_count
FROM portfolio_billing_line l
LEFT JOIN portfolio_control_result r
    ON r.line_id = l.line_id
WHERE r.line_id IS NULL

UNION ALL

SELECT 'NEGATIVE_EXPECTED_AMOUNT', COUNT(*)
FROM portfolio_billing_line
WHERE expected_amount < 0

UNION ALL

SELECT 'NEGATIVE_BILLED_AMOUNT', COUNT(*)
FROM portfolio_billing_line
WHERE billed_amount < 0

UNION ALL

SELECT 'STRONG_CONTROL_PENDING', COUNT(*)
FROM portfolio_billing_line l
INNER JOIN portfolio_billing_concept c
    ON c.concept_code = l.concept_code
LEFT JOIN portfolio_control_result r
    ON r.line_id = l.line_id
WHERE c.strong_control_flag = 'Y'
  AND NVL(r.control_status, 'PENDING') = 'PENDING';
