-- Self-contained Oracle SQL illustration, fictitious data only.
-- No DDL, production objects, credentials or external source access.
-- Not executed as part of the Python tests.
WITH expected_lines (student_ref, program_ref, amount) AS (
    SELECT 'SYN-S001', 'SYN-A', 100 FROM dual UNION ALL
    SELECT 'SYN-S001', 'SYN-B',  50 FROM dual
),
actual_lines (student_ref, program_ref, amount) AS (
    SELECT 'SYN-S001', 'SYN-A', 150 FROM dual
),
expected AS (
    SELECT student_ref, program_ref, COUNT(*) line_count, SUM(amount) amount
    FROM expected_lines GROUP BY student_ref, program_ref
),
actual AS (
    SELECT student_ref, program_ref, COUNT(*) line_count, SUM(amount) amount
    FROM actual_lines GROUP BY student_ref, program_ref
)
SELECT COALESCE(e.student_ref, a.student_ref) student_ref,
       COALESCE(e.program_ref, a.program_ref) program_ref,
       NVL(a.line_count, 0) - NVL(e.line_count, 0) line_difference,
       ROUND((NVL(a.amount, 0) - NVL(e.amount, 0)) * 100) difference_cents
FROM expected e
FULL OUTER JOIN actual a
  ON a.student_ref = e.student_ref AND a.program_ref = e.program_ref
ORDER BY student_ref, program_ref;
