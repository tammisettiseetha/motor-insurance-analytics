import pandas as pd

from src.insurance_analysis import _safe_divide
from src.insights import (
    generate_portfolio_insights,
    generate_claim_insights,
)


def test_safe_divide():
    assert _safe_divide(10, 2) == 5


def test_safe_divide_by_zero():
    assert _safe_divide(10, 0) == 0


def test_portfolio_insights():
    data = {
        "policies": pd.DataFrame({"policy_id": [1, 2]}),
        "customers": pd.DataFrame({"customer_id": [10, 11, 12]}),
    }

    insights = generate_portfolio_insights(data)

    assert any("2" in item for item in insights)
    assert any("3" in item for item in insights)


def test_claim_insights():
    data = {
        "claims": pd.DataFrame({
            "claim_id": [1, 2],
            "claim_status": ["Approved", "Pending"],
        })
    }

    insights = generate_claim_insights(data)

    assert any("Total claims: 2" in item for item in insights)