"""Illustrative Oracle extraction using environment variables.

Map the placeholder views and fields to an authorized environment before use.
Never hard-code credentials in source code or notebooks.
"""

import os

import pandas as pd
from sqlalchemy import create_engine, text


required_variables = ["ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
missing = [name for name in required_variables if not os.getenv(name)]
if missing:
    raise RuntimeError(f"Missing environment variables: {', '.join(missing)}")

engine = create_engine(
    "oracle+oracledb://",
    connect_args={
        "user": os.environ["ORACLE_USER"],
        "password": os.environ["ORACLE_PASSWORD"],
        "dsn": os.environ["ORACLE_DSN"],
    },
)

period = "2026-01"
expected_query = text(
    """
    SELECT account_ref, expected_line_count, expected_amount
    FROM portfolio_expected_scope
    WHERE billing_period = :billing_period
    """
)
billed_query = text(
    """
    SELECT account_ref, billed_line_count, billed_amount, justification_type
    FROM portfolio_billed_scope
    WHERE billing_period = :billing_period
    """
)

with engine.connect() as connection:
    expected_scope = pd.read_sql(
        expected_query, connection, params={"billing_period": period}
    )
    billed_scope = pd.read_sql(
        billed_query, connection, params={"billing_period": period}
    )
