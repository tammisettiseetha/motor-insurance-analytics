import pandas as pd


def _get_table(data, table_name):
    """Return a copy of a table if it exists."""
    df = data.get(table_name)

    if not isinstance(df, pd.DataFrame):
        return pd.DataFrame()

    return df.copy()


def generate_portfolio_insights(data):
    """Summarize the overall insurance portfolio."""
    policies = _get_table(data, "policies")
    customers = _get_table(data, "customers")

    insights = []

    insights.append(f"Total policies: {len(policies):,}")
    insights.append(f"Total customers: {len(customers):,}")

    return insights


def generate_claim_insights(data):
    """Summarize claim volume and available claim statuses."""
    claims = _get_table(data, "claims")
    insights = [f"Total claims: {len(claims):,}"]

    if "claim_status" in claims.columns:
        statuses = claims["claim_status"].fillna("Unknown").value_counts()

        for status, count in statuses.items():
            insights.append(f"Claims with status '{status}': {count:,}")

    return insights


def generate_premium_insights(data):
    """Summarize premium information when available."""
    policies = _get_table(data, "policies")
    insights = []

    premium_column = next(
        (
            column for column in policies.columns
            if "premium" in column.lower()
        ),
        None,
    )

    if premium_column:
        premiums = pd.to_numeric(
            policies[premium_column], errors="coerce"
        ).dropna()

        if not premiums.empty:
            insights.append(
                f"Average {premium_column}: {premiums.mean():,.2f}"
            )
            insights.append(
                f"Total {premium_column}: {premiums.sum():,.2f}"
            )

    return insights


def generate_customer_insights(data):
    """Summarize customer records."""
    customers = _get_table(data, "customers")

    return [f"Total customer records: {len(customers):,}"]


def generate_vehicle_insights(data):
    """Summarize vehicle records."""
    vehicles = _get_table(data, "vehicles")

    return [f"Total vehicle records: {len(vehicles):,}"]


def generate_risk_patterns(data):
    """Identify possible risk patterns from available claim fields."""
    claims = _get_table(data, "claims")
    vehicles = _get_table(data, "vehicles")
    insights = []

    if "claim_amount" in claims.columns:
        amounts = pd.to_numeric(
            claims["claim_amount"], errors="coerce"
        ).dropna()

        if not amounts.empty:
            threshold = amounts.quantile(0.90)
            high_value_count = int((amounts >= threshold).sum())

            insights.append(
                f"{high_value_count:,} claims are at or above "
                f"the 90th-percentile claim amount ({threshold:,.2f})."
            )

    if vehicles.empty:
        insights.append("Vehicle data is unavailable for risk analysis.")

    return insights


def generate_business_recommendations(data):
    """Generate preliminary recommendations based on available data."""
    claims = _get_table(data, "claims")
    policies = _get_table(data, "policies")
    recommendations = []

    if not claims.empty:
        recommendations.append(
            "Review claim processing times and pending claims "
            "to identify possible service delays."
        )

    if not policies.empty:
        recommendations.append(
            "Compare premium amounts across available policy categories "
            "to understand portfolio composition."
        )

    if not recommendations:
        recommendations.append(
            "Load the cleaned insurance datasets before generating "
            "business recommendations."
        )

    return recommendations