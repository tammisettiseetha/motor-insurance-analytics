import pandas as pd


def _get_table(data, table_name):
    """Get a copy of a dataset."""
    if table_name not in data:
        raise KeyError(f"Dataset not found: {table_name}")

    return data[table_name].copy()


def _numeric_values(df, column):
    """Convert a column to numeric values for calculations."""
    if column not in df.columns:
        raise ValueError(f"Required column not found: {column}")

    return pd.to_numeric(df[column], errors="coerce")


def _safe_divide(numerator, denominator):
    """Avoid division by zero."""
    if denominator == 0:
        return 0

    return numerator / denominator


def _status_counts(df, column):
    """Count status values, including missing statuses."""
    if column not in df.columns:
        return pd.Series(dtype="int64")

    return (
        df[column]
        .fillna("Unknown")
        .astype(str)
        .str.strip()
        .replace("", "Unknown")
        .value_counts()
    )


# ---------------- POLICY ANALYSIS ----------------

def calculate_total_policies(data):
    policies = _get_table(data, "policies")
    return int(policies["policy_id"].nunique())


def calculate_active_policies(data):
    policies = _get_table(data, "policies")
    status = policies["policy_status"].astype("string").str.strip().str.lower()

    return int(status.eq("active").sum())


def calculate_policy_status_distribution(data):
    policies = _get_table(data, "policies")
    return _status_counts(policies, "policy_status")


def calculate_total_premium(data):
    policies = _get_table(data, "policies")
    return float(_numeric_values(policies, "premium_amount").sum())


def calculate_average_premium(data):
    policies = _get_table(data, "policies")
    return float(_numeric_values(policies, "premium_amount").mean())


def calculate_total_coverage_amount(data):
    policies = _get_table(data, "policies")
    return float(_numeric_values(policies, "coverage_amount").sum())


def calculate_premium_by_policy_type(data):
    policies = _get_table(data, "policies")
    df = policies.assign(
        premium=_numeric_values(policies, "premium_amount")
    )

    return df.groupby("policy_type", dropna=False)["premium"].sum().sort_values(
        ascending=False
    )


# ---------------- CUSTOMER ANALYSIS ----------------

def calculate_total_customers(data):
    customers = _get_table(data, "customers")
    return int(customers["customer_id"].nunique())


def calculate_customer_gender_distribution(data):
    customers = _get_table(data, "customers")
    return _status_counts(customers, "gender")


def calculate_customer_city_distribution(data):
    customers = _get_table(data, "customers")
    return _status_counts(customers, "city")


def calculate_average_customer_age(data):
    customers = _get_table(data, "customers")
    ages = _numeric_values(customers, "age")
    ages = ages[ages.between(0, 120)]

    return float(ages.mean())


# ---------------- VEHICLE ANALYSIS ----------------

def calculate_total_vehicles(data):
    vehicles = _get_table(data, "vehicles")
    return int(vehicles["vehicle_id"].nunique())


def calculate_vehicle_type_distribution(data):
    vehicles = _get_table(data, "vehicles")
    return _status_counts(vehicles, "vehicle_type")


def calculate_vehicle_fuel_distribution(data):
    vehicles = _get_table(data, "vehicles")
    return _status_counts(vehicles, "fuel_type")


def calculate_total_vehicle_value(data):
    vehicles = _get_table(data, "vehicles")
    return float(_numeric_values(vehicles, "vehicle_value").sum())


# ---------------- CLAIM ANALYSIS ----------------

def calculate_total_claims(data):
    claims = _get_table(data, "claims")
    return int(claims["claim_id"].nunique())


def calculate_total_claim_amount(data):
    claims = _get_table(data, "claims")
    return float(_numeric_values(claims, "claim_amount").sum())


def calculate_average_claim_amount(data):
    claims = _get_table(data, "claims")
    return float(_numeric_values(claims, "claim_amount").mean())


def calculate_claim_status_distribution(data):
    claims = _get_table(data, "claims")
    return _status_counts(claims, "claim_status")


def calculate_claim_type_distribution(data):
    claims = _get_table(data, "claims")
    return _status_counts(claims, "claim_type")


def calculate_claim_approval_rate(data):
    claims = _get_table(data, "claims")
    status = claims["claim_status"].astype("string").str.strip().str.lower()

    recorded = status.notna() & status.ne("")
    approved = status.str.contains("approv", na=False)

    return float(
        _safe_divide(approved[recorded].sum(), recorded.sum()) * 100
    )


def calculate_claim_rejection_rate(data):
    claims = _get_table(data, "claims")
    status = claims["claim_status"].astype("string").str.strip().str.lower()

    recorded = status.notna() & status.ne("")
    rejected = status.str.contains("reject|denied|declined", na=False)

    return float(
        _safe_divide(rejected[recorded].sum(), recorded.sum()) * 100
    )


def calculate_claim_settlement_rate(data):
    """Percentage of claims with a recorded settlement date."""
    claims = _get_table(data, "claims")
    settlement_dates = pd.to_datetime(
        claims["settlement_date"], errors="coerce"
    )

    total_claims = len(claims)

    return float(
        _safe_divide(settlement_dates.notna().sum(), total_claims) * 100
    )


def calculate_average_claim_settlement_days(data):
    """Average calendar days from claim date to settlement."""
    claims = _get_table(data, "claims")

    claim_dates = pd.to_datetime(claims["claim_date"], errors="coerce")
    settlement_dates = pd.to_datetime(
        claims["settlement_date"], errors="coerce"
    )

    days = (settlement_dates - claim_dates).dt.days
    valid_days = days[days >= 0].dropna()

    return float(valid_days.mean())


def calculate_claim_amount_to_premium_ratio(data):
    """Compare total claimed amount with total policy premium."""
    total_claim_amount = calculate_total_claim_amount(data)
    total_premium = calculate_total_premium(data)

    return float(_safe_divide(total_claim_amount, total_premium) * 100)


# ---------------- PAYMENT ANALYSIS ----------------

def calculate_payment_count(data):
    payments = _get_table(data, "payments")
    return int(payments["payment_id"].nunique())


def calculate_total_payment_amount(data):
    payments = _get_table(data, "payments")
    return float(_numeric_values(payments, "payment_amount").sum())


def calculate_average_payment_amount(data):
    payments = _get_table(data, "payments")
    return float(_numeric_values(payments, "payment_amount").mean())


def calculate_payment_status_distribution(data):
    payments = _get_table(data, "payments")
    return _status_counts(payments, "payment_status")


def calculate_payment_method_distribution(data):
    payments = _get_table(data, "payments")
    return _status_counts(payments, "payment_method")


def calculate_completed_payment_amount(data):
    """Sum payment amounts whose status indicates completion."""
    payments = _get_table(data, "payments")
    status = (
        payments["payment_status"]
        .astype("string")
        .str.strip()
        .str.lower()
    )

    completed = status.isin(["completed", "successful", "success", "paid"])
    amounts = _numeric_values(payments, "payment_amount")

    return float(amounts[completed].sum())


# ---------------- COMBINED KPI SUMMARY ----------------

def calculate_all_kpis(data):
    """Return a dictionary containing the main portfolio KPIs."""
    return {
        "Total Customers": calculate_total_customers(data),
        "Total Vehicles": calculate_total_vehicles(data),
        "Total Policies": calculate_total_policies(data),
        "Active Policies": calculate_active_policies(data),
        "Total Premium": calculate_total_premium(data),
        "Average Premium": calculate_average_premium(data),
        "Total Coverage Amount": calculate_total_coverage_amount(data),
        "Total Claims": calculate_total_claims(data),
        "Total Claim Amount": calculate_total_claim_amount(data),
        "Average Claim Amount": calculate_average_claim_amount(data),
        "Claim Approval Rate (%)": calculate_claim_approval_rate(data),
        "Claim Rejection Rate (%)": calculate_claim_rejection_rate(data),
        "Claim Settlement Rate (%)": calculate_claim_settlement_rate(data),
        "Average Settlement Days": calculate_average_claim_settlement_days(data),
        "Claim Amount to Premium Ratio (%)": (
            calculate_claim_amount_to_premium_ratio(data)
        ),
        "Payment Count": calculate_payment_count(data),
        "Total Payment Amount": calculate_total_payment_amount(data),
        "Completed Payment Amount": calculate_completed_payment_amount(data),
    }

# ---------------- CUSTOMER ANALYSIS ----------------

def analyze_customer_claims(data):
    """Summarize claims and claim amounts for each customer."""
    customers = _get_table(data, "customers")
    claims = _get_table(data, "claims")

    claims["claim_amount"] = _numeric(claims, "claim_amount")

    summary = (
        claims.groupby("customer_id", dropna=False)
        .agg(
            claim_count=("claim_id", "nunique"),
            total_claim_amount=("claim_amount", "sum"),
            average_claim_amount=("claim_amount", "mean"),
        )
        .reset_index()
    )

    result = customers.merge(summary, on="customer_id", how="left")
    result["claim_count"] = result["claim_count"].fillna(0)
    result["total_claim_amount"] = result["total_claim_amount"].fillna(0)

    return result


def analyze_customer_premium(data):
    """Summarize policy counts and premiums for each customer."""
    customers = _get_table(data, "customers")
    policies = _get_table(data, "policies")

    policies["premium_amount"] = _numeric(
        policies, "premium_amount"
    )

    summary = (
        policies.groupby("customer_id", dropna=False)
        .agg(
            policy_count=("policy_id", "nunique"),
            total_premium=("premium_amount", "sum"),
            average_premium=("premium_amount", "mean"),
        )
        .reset_index()
    )

    result = customers.merge(summary, on="customer_id", how="left")
    result["policy_count"] = result["policy_count"].fillna(0)
    result["total_premium"] = result["total_premium"].fillna(0)

    return result


# ---------------- VEHICLE ANALYSIS ----------------

def _build_vehicle_claim_detail(data):
    """Connect claim records to vehicle details through policy IDs."""
    claims = _get_table(data, "claims")
    policies = _get_table(data, "policies")
    vehicles = _get_table(data, "vehicles")

    claims["claim_amount"] = _numeric(
        claims, "claim_amount"
    )

    policy_vehicle = policies[
        ["policy_id", "vehicle_id"]
    ].drop_duplicates("policy_id")

    vehicle_details = vehicles[
        [
            "vehicle_id",
            "vehicle_type",
            "vehicle_make",
            "vehicle_model",
            "vehicle_year",
            "fuel_type",
        ]
    ].drop_duplicates("vehicle_id")

    detail = claims.merge(
        policy_vehicle, on="policy_id", how="left"
    )

    return detail.merge(
        vehicle_details, on="vehicle_id", how="left"
    )


def analyze_vehicle_claims(data):
    """Summarize claim counts and amounts for each vehicle."""
    vehicles = _get_table(data, "vehicles")
    detail = _build_vehicle_claim_detail(data)

    summary = (
        detail.groupby("vehicle_id", dropna=False)
        .agg(
            claim_count=("claim_id", "nunique"),
            total_claim_amount=("claim_amount", "sum"),
            average_claim_amount=("claim_amount", "mean"),
        )
        .reset_index()
    )

    result = vehicles.merge(summary, on="vehicle_id", how="left")
    result["claim_count"] = result["claim_count"].fillna(0)
    result["total_claim_amount"] = (
        result["total_claim_amount"].fillna(0)
    )

    return result


def analyze_vehicle_risk_patterns(data):
    """Compare vehicle claim amounts with associated premiums."""
    vehicle_summary = analyze_vehicle_claims(data)
    policies = _get_table(data, "policies")

    policies["premium_amount"] = _numeric(
        policies, "premium_amount"
    )

    premium_summary = (
        policies.groupby("vehicle_id", dropna=False)
        .agg(
            policy_count=("policy_id", "nunique"),
            total_premium=("premium_amount", "sum"),
        )
        .reset_index()
    )

    result = vehicle_summary.merge(
        premium_summary, on="vehicle_id", how="left"
    )

    result["total_premium"] = result["total_premium"].fillna(0)

    result["claim_to_premium_ratio"] = (
        result["total_claim_amount"]
        / result["total_premium"].where(
            result["total_premium"] != 0
        )
    )

    current_year = pd.Timestamp.today().year
    result["vehicle_age"] = (
        current_year
        - pd.to_numeric(result["vehicle_year"], errors="coerce")
    )

    return result.sort_values(
        "claim_to_premium_ratio",
        ascending=False,
        na_position="last",
    )


def analyze_vehicle_type(data):
    """Summarize claim frequency and amounts by vehicle type."""
    vehicles = _get_table(data, "vehicles")
    detail = _build_vehicle_claim_detail(data)

    vehicle_counts = (
        vehicles.groupby("vehicle_type", dropna=False)["vehicle_id"]
        .nunique()
        .rename("vehicle_count")
    )

    claim_summary = (
        detail.groupby("vehicle_type", dropna=False)
        .agg(
            claim_count=("claim_id", "nunique"),
            total_claim_amount=("claim_amount", "sum"),
            average_claim_amount=("claim_amount", "mean"),
        )
    )

    return (
        vehicle_counts.to_frame()
        .join(claim_summary, how="outer")
        .fillna(0)
        .sort_values("total_claim_amount", ascending=False)
        .reset_index()
    )