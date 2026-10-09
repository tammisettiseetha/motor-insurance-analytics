

import matplotlib.pyplot as plt
import pandas as pd


# -------------------- SHARED HELPERS --------------------

def _require_columns(df, columns):
    """Check whether the required columns exist."""
    missing = [column for column in columns if column not in df.columns]

    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def _numeric(df, column):
    """Convert a column to numeric values."""
    _require_columns(df, [column])
    return pd.to_numeric(df[column], errors="coerce")


def _category_counts(df, column):
    """Count categories, including missing values."""
    _require_columns(df, [column])

    values = (
        df[column]
        .astype("string")
        .str.strip()
        .fillna("Unknown")
        .replace("", "Unknown")
    )

    return values.value_counts()


def _bar_chart(series, title, xlabel, ylabel, horizontal=False):
    """Create and return a labeled bar chart."""
    fig, ax = plt.subplots(figsize=(9, 5))

    if series.empty:
        ax.text(0.5, 0.5, "No data available",
                ha="center", va="center")
        ax.set_axis_off()
    elif horizontal:
        series.sort_values().plot(kind="barh", ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
    else:
        series.plot(kind="bar", ax=ax)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.tick_params(axis="x", rotation=30)

    ax.set_title(title)
    fig.tight_layout()
    return fig


def _claim_vehicle_detail(claims, policies, vehicles):
    """Join claims with their policy and vehicle details."""
    _require_columns(claims, ["claim_id", "policy_id", "claim_amount"])
    _require_columns(policies, ["policy_id", "vehicle_id"])
    _require_columns(vehicles, [
        "vehicle_id", "vehicle_type", "vehicle_make", "vehicle_year"
    ])

    policy_vehicle = policies[
        ["policy_id", "vehicle_id"]
    ].drop_duplicates("policy_id")

    vehicle_details = vehicles[
        ["vehicle_id", "vehicle_type", "vehicle_make", "vehicle_year"]
    ].drop_duplicates("vehicle_id")

    detail = claims.merge(
        policy_vehicle, on="policy_id", how="left"
    )

    detail = detail.merge(
        vehicle_details, on="vehicle_id", how="left"
    )

    detail["claim_amount"] = _numeric(detail, "claim_amount")
    return detail


def _claim_region_detail(claims, customers):
    """Join claims to customer state and city."""
    _require_columns(claims, [
        "claim_id", "customer_id", "claim_amount"
    ])
    _require_columns(customers, ["customer_id", "state", "city"])

    customer_locations = customers[
        ["customer_id", "state", "city"]
    ].drop_duplicates("customer_id")

    detail = claims.merge(
        customer_locations, on="customer_id", how="left"
    )

    detail["claim_amount"] = _numeric(detail, "claim_amount")

    detail["region"] = (
        detail["state"].fillna("Unknown").astype(str)
        + " / "
        + detail["city"].fillna("Unknown").astype(str)
    )

    return detail


# -------------------- POLICY VISUALIZATIONS --------------------

def plot_policy_status(policies):
    """Show the number of policies by status."""
    counts = _category_counts(policies, "policy_status")
    return _bar_chart(
        counts, "Policies by Status",
        "Policy Status", "Number of Policies"
    )


def plot_policy_type_distribution(policies):
    """Show the number of policies by policy type."""
    counts = _category_counts(policies, "policy_type")
    return _bar_chart(
        counts, "Policy Type Distribution",
        "Policy Type", "Number of Policies"
    )


def plot_premium_by_policy_type(policies):
    """Compare total premium across policy types."""
    _require_columns(policies, ["policy_type", "premium_amount"])

    df = policies.copy()
    df["premium_amount"] = _numeric(df, "premium_amount")

    totals = (
        df.groupby("policy_type", dropna=False)["premium_amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return _bar_chart(
        totals, "Total Premium by Policy Type",
        "Policy Type", "Total Premium"
    )


# -------------------- CLAIM VISUALIZATIONS --------------------

def plot_monthly_claims(claims):
    """Show claim counts by claim month."""
    _require_columns(claims, ["claim_date"])

    dates = pd.to_datetime(claims["claim_date"], errors="coerce").dropna()

    monthly = dates.dt.to_period("M").value_counts().sort_index()
    monthly.index = monthly.index.astype(str)

    fig, ax = plt.subplots(figsize=(10, 5))

    if monthly.empty:
        ax.text(0.5, 0.5, "No valid claim dates available",
                ha="center", va="center")
        ax.set_axis_off()
    else:
        monthly.plot(kind="line", marker="o", ax=ax)
        ax.set_xlabel("Claim Month")
        ax.set_ylabel("Number of Claims")
        ax.tick_params(axis="x", rotation=45)

    ax.set_title("Monthly Claim Volume")
    fig.tight_layout()
    return fig


def plot_claim_status(claims):
    """Show the number of claims by status."""
    counts = _category_counts(claims, "claim_status")
    return _bar_chart(
        counts, "Claims by Status",
        "Claim Status", "Number of Claims"
    )


def plot_claim_type_distribution(claims):
    """Show the number of claims by claim type."""
    counts = _category_counts(claims, "claim_type")
    return _bar_chart(
        counts, "Claim Type Distribution",
        "Claim Type", "Number of Claims"
    )


def plot_claim_amount_distribution(claims):
    """Show the distribution of claim amounts."""
    amounts = _numeric(claims, "claim_amount").dropna()

    fig, ax = plt.subplots(figsize=(9, 5))

    if amounts.empty:
        ax.text(0.5, 0.5, "No valid claim amounts available",
                ha="center", va="center")
        ax.set_axis_off()
    else:
        ax.hist(amounts, bins=25)
        ax.set_xlabel("Claim Amount")
        ax.set_ylabel("Frequency")

    ax.set_title("Claim Amount Distribution")
    fig.tight_layout()
    return fig


def plot_claim_amount_by_vehicle_type(claims, policies, vehicles):
    """Compare total claim amount across vehicle types."""
    detail = _claim_vehicle_detail(claims, policies, vehicles)

    totals = (
        detail.groupby("vehicle_type", dropna=False)["claim_amount"]
        .sum()
        .sort_values(ascending=False)
    )

    return _bar_chart(
        totals, "Total Claim Amount by Vehicle Type",
        "Vehicle Type", "Total Claim Amount"
    )


def plot_claims_by_region(claims, customers):
    """Compare claim counts across customer state/city regions."""
    detail = _claim_region_detail(claims, customers)

    counts = (
        detail.groupby("region", dropna=False)["claim_id"]
        .nunique()
        .sort_values(ascending=False)
        .head(15)
    )

    return _bar_chart(
        counts, "Top Regions by Claim Count",
        "Number of Claims", "State / City", horizontal=True
    )


def plot_claim_severity_by_region(claims, customers):
    """Compare average claim amount by state/city region."""
    detail = _claim_region_detail(claims, customers)

    averages = (
        detail.groupby("region", dropna=False)["claim_amount"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
        .head(15)
    )

    return _bar_chart(
        averages, "Average Claim Amount by Region",
        "Average Claim Amount", "State / City", horizontal=True
    )


def plot_average_settlement_time(claims):
    """Compare average settlement days across claim statuses."""
    _require_columns(
        claims, ["claim_date", "settlement_date", "claim_status"]
    )

    df = claims.copy()
    df["claim_date"] = pd.to_datetime(
        df["claim_date"], errors="coerce"
    )
    df["settlement_date"] = pd.to_datetime(
        df["settlement_date"], errors="coerce"
    )

    df["settlement_days"] = (
        df["settlement_date"] - df["claim_date"]
    ).dt.days

    # Exclude missing and negative settlement durations.
    df.loc[df["settlement_days"] < 0, "settlement_days"] = pd.NA

    averages = (
        df.groupby("claim_status", dropna=False)["settlement_days"]
        .mean()
        .dropna()
        .sort_values(ascending=False)
    )

    return _bar_chart(
        averages, "Average Settlement Time by Claim Status",
        "Claim Status", "Average Settlement Days"
    )


def plot_claim_to_premium_by_policy_type(claims, policies):
    """Compare total claim amount with total premium by policy type."""
    _require_columns(
        claims, ["policy_id", "claim_amount"]
    )
    _require_columns(
        policies, ["policy_id", "policy_type", "premium_amount"]
    )

    claim_data = claims[
        ["policy_id", "claim_amount"]
    ].copy()

    claim_data["claim_amount"] = _numeric(
        claim_data, "claim_amount"
    )

    policy_types = policies[
        ["policy_id", "policy_type"]
    ].drop_duplicates("policy_id")

    claim_data = claim_data.merge(
        policy_types, on="policy_id", how="left"
    )

    claims_by_type = (
        claim_data.groupby("policy_type", dropna=False)["claim_amount"]
        .sum()
    )

    premium_data = policies.copy()
    premium_data["premium_amount"] = _numeric(
        premium_data, "premium_amount"
    )

    premiums_by_type = (
        premium_data.groupby("policy_type", dropna=False)["premium_amount"]
        .sum()
    )

    comparison = pd.concat(
        [
            claims_by_type.rename("claim_amount"),
            premiums_by_type.rename("premium_amount"),
        ],
        axis=1,
    ).fillna(0)

    comparison["claim_to_premium_ratio"] = (
        comparison["claim_amount"]
        / comparison["premium_amount"].where(
            comparison["premium_amount"] != 0
        )
    )

    ratios = (
        comparison["claim_to_premium_ratio"]
        .dropna()
        .sort_values(ascending=False)
    )

    return _bar_chart(
        ratios, "Claim-to-Premium Ratio by Policy Type",
        "Policy Type", "Claim Amount / Premium Amount"
    )


# -------------------- CUSTOMER / VEHICLE ANALYSIS --------------------

def plot_vehicle_age_vs_claim_amount(claims, policies, vehicles):
    """Show vehicle age at claim date against claim amount."""
    detail = _claim_vehicle_detail(claims, policies, vehicles)

    detail["claim_date"] = pd.to_datetime(
        detail["claim_date"], errors="coerce"
    )

    detail["vehicle_year"] = pd.to_numeric(
        detail["vehicle_year"], errors="coerce"
    )

    detail["vehicle_age"] = (
        detail["claim_date"].dt.year - detail["vehicle_year"]
    )

    plot_data = detail[
        ["vehicle_age", "claim_amount"]
    ].dropna()

    plot_data = plot_data[
        plot_data["vehicle_age"].between(0, 100)
        & (plot_data["claim_amount"] >= 0)
    ]

    fig, ax = plt.subplots(figsize=(9, 5))

    if plot_data.empty:
        ax.text(0.5, 0.5, "No valid vehicle-age and claim data",
                ha="center", va="center")
        ax.set_axis_off()
    else:
        ax.scatter(
            plot_data["vehicle_age"],
            plot_data["claim_amount"],
            alpha=0.5,
        )
        ax.set_xlabel("Vehicle Age at Claim (Years)")
        ax.set_ylabel("Claim Amount")

    ax.set_title("Vehicle Age vs Claim Amount")
    fig.tight_layout()
    return fig


def plot_customer_age_vs_claim_amount(claims, customers):
    """Show customer age against claim amount."""
    _require_columns(
        claims, ["customer_id", "claim_amount"]
    )
    _require_columns(
        customers, ["customer_id", "age"]
    )

    customer_ages = customers[
        ["customer_id", "age"]
    ].drop_duplicates("customer_id")

    detail = claims.merge(
        customer_ages, on="customer_id", how="left"
    )

    detail["age"] = pd.to_numeric(detail["age"], errors="coerce")
    detail["claim_amount"] = _numeric(detail, "claim_amount")

    plot_data = detail.dropna(subset=["age", "claim_amount"])
    plot_data = plot_data[plot_data["age"].between(0, 120)]

    fig, ax = plt.subplots(figsize=(9, 5))

    if plot_data.empty:
        ax.text(0.5, 0.5, "No valid customer-age and claim data",
                ha="center", va="center")
        ax.set_axis_off()
    else:
        ax.scatter(
            plot_data["age"],
            plot_data["claim_amount"],
            alpha=0.5,
        )
        ax.set_xlabel("Customer Age")
        ax.set_ylabel("Claim Amount")

    ax.set_title("Customer Age vs Claim Amount")
    fig.tight_layout()
    return fig


def plot_vehicle_type_claim_performance(claims, policies, vehicles):
    """Compare claim frequency per 100 vehicles by vehicle type."""
    detail = _claim_vehicle_detail(claims, policies, vehicles)

    claim_counts = (
        detail.groupby("vehicle_type", dropna=False)["claim_id"]
        .nunique()
        .rename("claim_count")
    )

    vehicle_counts = (
        vehicles.groupby("vehicle_type", dropna=False)["vehicle_id"]
        .nunique()
        .rename("vehicle_count")
    )

    summary = pd.concat(
        [claim_counts, vehicle_counts], axis=1
    ).fillna(0)

    summary["claims_per_100_vehicles"] = (
        summary["claim_count"] / summary["vehicle_count"].where(
            summary["vehicle_count"] != 0
        ) * 100
    )

    rates = (
        summary["claims_per_100_vehicles"]
        .dropna()
        .sort_values(ascending=False)
    )

    return _bar_chart(
        rates, "Claim Frequency per 100 Vehicles",
        "Vehicle Type", "Claims per 100 Vehicles"
    )


def plot_damage_severity_distribution(claims):
    """Show the number of claims for each damage severity."""
    counts = _category_counts(claims, "damage_severity")

    return _bar_chart(
        counts, "Damage Severity Distribution",
        "Damage Severity", "Number of Claims"
    )


# -------------------- PAYMENT / PREMIUM TREND --------------------

def plot_payment_status(payments):
    """Show the number of payments by status."""
    counts = _category_counts(payments, "payment_status")

    return _bar_chart(
        counts, "Payment Status Distribution",
        "Payment Status", "Number of Payments"
    )


def plot_monthly_premium_trend(policies):
    """Show total premium by policy start month."""
    _require_columns(
        policies, ["policy_start_date", "premium_amount"]
    )

    df = policies.copy()
    df["policy_start_date"] = pd.to_datetime(
        df["policy_start_date"], errors="coerce"
    )
    df["premium_amount"] = _numeric(df, "premium_amount")
    df = df.dropna(subset=["policy_start_date", "premium_amount"])

    monthly = (
        df.set_index("policy_start_date")
        .resample("MS")["premium_amount"]
        .sum()
    )

    fig, ax = plt.subplots(figsize=(10, 5))

    if monthly.empty:
        ax.text(0.5, 0.5, "No valid policy dates or premium values",
                ha="center", va="center")
        ax.set_axis_off()
    else:
        monthly.plot(kind="line", marker="o", ax=ax)
        ax.set_xlabel("Policy Start Month")
        ax.set_ylabel("Total Premium")
        ax.tick_params(axis="x", rotation=45)

    ax.set_title("Monthly Premium Trend")
    fig.tight_layout()
    return fig