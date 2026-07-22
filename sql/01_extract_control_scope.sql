-- Representative Oracle SQL extraction used as the ACL input scope.

SELECT
    TO_CHAR(TRUNC(p.billing_month, 'MM'), 'YYYY-MM') AS billing_period,
    l.line_id,
    l.account_ref,
    SUBSTR(l.account_ref, 1, 3) AS account_group,
    l.concept_code,
    c.concept_name,
    l.expected_amount,
    l.billed_amount,
    c.strong_control_flag,
    NVL(r.control_status, 'PENDING') AS control_status,
    r.exception_reason
FROM portfolio_billing_line l
INNER JOIN portfolio_billing_period p
    ON p.period_id = l.period_id
INNER JOIN portfolio_billing_concept c
    ON c.concept_code = l.concept_code
LEFT JOIN portfolio_control_result r
    ON r.line_id = l.line_id
WHERE p.billing_month >= TO_DATE(:period_from, 'YYYY-MM-DD')
  AND p.billing_month < ADD_MONTHS(
      TO_DATE(:period_from, 'YYYY-MM-DD'),
      1
  )
ORDER BY l.line_id;
