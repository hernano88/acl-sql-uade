-- Synthetic Oracle schema for the public portfolio example.
-- Run in a disposable development schema. No production objects are referenced.

CREATE TABLE portfolio_billing_period (
    period_id      NUMBER       PRIMARY KEY,
    billing_month  DATE         NOT NULL
);

CREATE TABLE portfolio_billing_concept (
    concept_code        VARCHAR2(40) PRIMARY KEY,
    concept_name        VARCHAR2(100) NOT NULL,
    strong_control_flag CHAR(1)      NOT NULL,
    CONSTRAINT chk_portfolio_control_flag
        CHECK (strong_control_flag IN ('Y', 'N'))
);

CREATE TABLE portfolio_billing_line (
    line_id         NUMBER        PRIMARY KEY,
    period_id       NUMBER        NOT NULL,
    account_ref     VARCHAR2(20)  NOT NULL,
    concept_code    VARCHAR2(40)  NOT NULL,
    expected_amount NUMBER(14, 2) NOT NULL,
    billed_amount   NUMBER(14, 2) NOT NULL,
    CONSTRAINT fk_portfolio_line_period
        FOREIGN KEY (period_id) REFERENCES portfolio_billing_period(period_id),
    CONSTRAINT fk_portfolio_line_concept
        FOREIGN KEY (concept_code) REFERENCES portfolio_billing_concept(concept_code)
);

CREATE TABLE portfolio_control_result (
    line_id          NUMBER       PRIMARY KEY,
    control_status   VARCHAR2(30) NOT NULL,
    exception_reason VARCHAR2(100),
    CONSTRAINT fk_portfolio_result_line
        FOREIGN KEY (line_id) REFERENCES portfolio_billing_line(line_id)
);

INSERT INTO portfolio_billing_period VALUES (1, DATE '2026-07-01');

INSERT INTO portfolio_billing_concept VALUES
    ('COURSE_TUITION', 'Course tuition', 'Y');
INSERT INTO portfolio_billing_concept VALUES
    ('ENROLLMENT_FEE', 'Enrollment fee', 'Y');
INSERT INTO portfolio_billing_concept VALUES
    ('PROGRAM_FEE', 'Program fee', 'Y');
INSERT INTO portfolio_billing_concept VALUES
    ('SCHOLARSHIP_ADJUSTMENT', 'Scholarship adjustment', 'Y');
INSERT INTO portfolio_billing_concept VALUES
    ('DISCOUNT_ADJUSTMENT', 'Discount adjustment', 'Y');
INSERT INTO portfolio_billing_concept VALUES
    ('LOW_VOLUME_EXCEPTION', 'Low-volume exception', 'N');

INSERT INTO portfolio_billing_line VALUES
    (1, 1, 'ACC-0001', 'COURSE_TUITION', 42100, 42000);
INSERT INTO portfolio_billing_line VALUES
    (2, 1, 'ACC-0002', 'ENROLLMENT_FEE', 25000, 25000);
INSERT INTO portfolio_billing_line VALUES
    (3, 1, 'ACC-0003', 'PROGRAM_FEE', 17950, 18000);
INSERT INTO portfolio_billing_line VALUES
    (4, 1, 'ACC-0004', 'SCHOLARSHIP_ADJUSTMENT', 8000, 8000);
INSERT INTO portfolio_billing_line VALUES
    (5, 1, 'ACC-0005', 'DISCOUNT_ADJUSTMENT', 4950, 5000);
INSERT INTO portfolio_billing_line VALUES
    (6, 1, 'ACC-0006', 'LOW_VOLUME_EXCEPTION', 2000, 2000);

INSERT INTO portfolio_control_result VALUES (1, 'RECONCILED', NULL);
INSERT INTO portfolio_control_result VALUES (2, 'RECONCILED', NULL);
INSERT INTO portfolio_control_result VALUES
    (3, 'JUSTIFIED', 'PERIOD_ADJUSTMENT');
INSERT INTO portfolio_control_result VALUES (4, 'RECONCILED', NULL);
INSERT INTO portfolio_control_result VALUES
    (5, 'JUSTIFIED', 'ROUNDING_RULE');
INSERT INTO portfolio_control_result VALUES
    (6, 'MANUAL_REVIEW', 'OUTSIDE_AUTOMATED_SCOPE');

COMMIT;
