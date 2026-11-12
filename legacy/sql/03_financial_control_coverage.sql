-- Financial coverage is based on billed value, not record count.

WITH coverage_base AS (
    SELECT
        l.billed_amount,
        c.strong_control_flag
    FROM portfolio_billing_line l
    INNER JOIN portfolio_billing_concept c
        ON c.concept_code = l.concept_code
)
SELECT
    SUM(ABS(billed_amount)) AS total_billed_amount,
    SUM(
        CASE
            WHEN strong_control_flag = 'Y' THEN ABS(billed_amount)
            ELSE 0
        END
    ) AS controlled_billed_amount,
    ROUND(
        100 * SUM(
            CASE
                WHEN strong_control_flag = 'Y' THEN ABS(billed_amount)
                ELSE 0
            END
        ) / NULLIF(SUM(ABS(billed_amount)), 0),
        2
    ) AS financial_control_coverage_pct
FROM coverage_base;

-- Expected synthetic result:
-- total_billed_amount            = 100000
-- controlled_billed_amount       =  98000
-- financial_control_coverage_pct =     98
