"""Optional extraction template. Fictitious objects; import has no side effects.

Never call against an environment without authorization. No connection is used by the demos.
"""
import os
import re


def extract_synthetic_scopes(period):
    """Read placeholder views using a bound period, disposing the engine afterward."""
    if not re.fullmatch(r"\d{4}-(0[1-9]|1[0-2])", period):
        raise ValueError("Period must be YYYY-MM")
    import pandas as pd
    from sqlalchemy import URL, create_engine, text

    required = ["ORACLE_USER", "ORACLE_PASSWORD", "ORACLE_DSN"]
    if any(not os.environ.get(name) for name in required):
        raise RuntimeError("Required Oracle environment configuration is missing")
    # URL/driver arguments handle reserved characters without interpolating a URL.
    engine = create_engine(
        URL.create("oracle+oracledb"),
        connect_args={
            "user": os.environ["ORACLE_USER"],
            "password": os.environ["ORACLE_PASSWORD"],
            "dsn": os.environ["ORACLE_DSN"],
        },
    )
    queries = {
        "expected": text("""
            SELECT row_id, student_ref, program_ref, period, amount
            FROM portfolio_synthetic_assigned
            WHERE period = :period
        """),
        "actual": text("""
            SELECT row_id, student_ref, program_ref, period, amount, manual_adjustment
            FROM portfolio_synthetic_billed
            WHERE period = :period
        """),
    }
    try:
        with engine.connect() as connection:
            return {
                name: pd.read_sql(query, connection, params={"period": period},
                                  coerce_float=False)
                for name, query in queries.items()
            }
    finally:
        engine.dispose()
