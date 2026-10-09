import pandas as pd


REQUIRED_COLUMNS = {
    "customers": [
        "customer_id",
    ],
    "vehicles": [
        "vehicle_id",
        "customer_id",
    ],
    "policies": [
        "policy_id",
        "customer_id",
        "vehicle_id",
    ],
    "claims": [
        "claim_id",
        "policy_id",
    ],
    "payments": [
        "payment_id",
        "policy_id",
    ],
}


def _validate_table(df, table_name):
    """Check that a table is a DataFrame with required columns."""
    errors = []

    if not isinstance(df, pd.DataFrame):
        return [f"{table_name}: expected a Pandas DataFrame"]

    missing_columns = [
        column
        for column in REQUIRED_COLUMNS[table_name]
        if column not in df.columns
    ]

    if missing_columns:
        errors.append(
            f"{table_name}: missing required columns {missing_columns}"
        )

    return errors


def validate_customers(df):
    return _validate_table(df, "customers")


def validate_vehicles(df):
    return _validate_table(df, "vehicles")


def validate_policies(df):
    return _validate_table(df, "policies")


def validate_claims(df):
    return _validate_table(df, "claims")


def validate_payments(df):
    return _validate_table(df, "payments")


def validate_relationships(data):
    """Check foreign-key relationships when the required columns exist."""
    errors = []

    relationships = [
        ("vehicles", "customer_id", "customers", "customer_id"),
        ("policies", "customer_id", "customers", "customer_id"),
        ("policies", "vehicle_id", "vehicles", "vehicle_id"),
        ("claims", "policy_id", "policies", "policy_id"),
        ("payments", "policy_id", "policies", "policy_id"),
    ]

    for child_name, child_key, parent_name, parent_key in relationships:
        child = data.get(child_name)
        parent = data.get(parent_name)

        if not isinstance(child, pd.DataFrame):
            continue
        if not isinstance(parent, pd.DataFrame):
            continue
        if child_key not in child.columns or parent_key not in parent.columns:
            continue

        parent_ids = parent[parent_key].dropna()
        unmatched = child[
            child[child_key].notna()
            & ~child[child_key].isin(parent_ids)
        ]

        if not unmatched.empty:
            errors.append(
                f"{child_name}.{child_key}: "
                f"{len(unmatched)} rows have no matching "
                f"{parent_name}.{parent_key}"
            )

    return errors


def validate_all_tables(data):
    """Validate all five tables and their relationships."""
    errors = []

    validators = {
        "customers": validate_customers,
        "vehicles": validate_vehicles,
        "policies": validate_policies,
        "claims": validate_claims,
        "payments": validate_payments,
    }

    for table_name, validator in validators.items():
        if table_name not in data:
            errors.append(f"Missing table: {table_name}")
        else:
            errors.extend(validator(data[table_name]))

    errors.extend(validate_relationships(data))

    return errors