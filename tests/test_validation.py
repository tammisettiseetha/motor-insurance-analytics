import pandas as pd

from src.validation import (
    validate_customers,
    validate_claims,
    validate_all_tables,
)


def test_validate_customers_with_required_column():
    df = pd.DataFrame({"customer_id": [1, 2]})
    assert validate_customers(df) == []


def test_validate_customers_detects_missing_column():
    df = pd.DataFrame({"name": ["A", "B"]})
    errors = validate_customers(df)
    assert len(errors) > 0


def test_validate_claims_with_required_columns():
    df = pd.DataFrame({
        "claim_id": [1],
        "policy_id": [101],
    })
    assert validate_claims(df) == []


def test_validate_all_tables_detects_missing_table():
    data = {}
    errors = validate_all_tables(data)
    assert any("Missing table" in error for error in errors)