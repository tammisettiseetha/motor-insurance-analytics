from pathlib import Path
import pandas as pd


def handle_missing_values(data):
    """Handle missing values conservatively without deleting rows."""
    cleaned = {}

    for table_name, df in data.items():
        df = df.copy()

        # Missing dates can be meaningful, especially for pending claims.
        # Do not automatically fill every missing value.
        if table_name == "customers":
            for column in df.select_dtypes(include=["object", "string"]).columns:
                if column != "customer_id":
                    df[column] = df[column].fillna("Unknown")

        cleaned[table_name] = df

    return cleaned


def remove_duplicates(data):
    """Remove completely duplicated rows from each table."""
    cleaned = {}

    for table_name, df in data.items():
        cleaned[table_name] = df.drop_duplicates().copy()

    return cleaned


def clean_text_columns(data):
    """Trim extra spaces in text columns."""
    cleaned = {}

    for table_name, df in data.items():
        df = df.copy()

        for column in df.select_dtypes(include=["object", "string"]).columns:
            df[column] = df[column].map(
                lambda value: value.strip() if isinstance(value, str) else value
            )

        cleaned[table_name] = df

    return cleaned


def clean_date_columns(data):
    """Convert columns with date-like names to datetime."""
    cleaned = {}

    for table_name, df in data.items():
        df = df.copy()

        for column in df.columns:
            if "date" in column.lower():
                df[column] = pd.to_datetime(df[column], errors="coerce")

        cleaned[table_name] = df

    return cleaned


def validate_numeric_columns(data):
    """Convert numeric-looking columns only when their names suggest numbers."""
    cleaned = {}

    numeric_terms = (
        "amount", "premium", "cost", "value", "age",
        "year", "score", "count", "quantity", "duration"
    )

    for table_name, df in data.items():
        df = df.copy()

        for column in df.columns:
            if any(term in column.lower() for term in numeric_terms):
                df[column] = pd.to_numeric(df[column], errors="coerce")

        cleaned[table_name] = df

    return cleaned


def validate_business_rules(data):
    """Flag obviously invalid negative financial values without deleting rows."""
    cleaned = {}

    financial_terms = ("premium", "amount", "cost", "payment", "claim")

    for table_name, df in data.items():
        df = df.copy()

        for column in df.columns:
            if any(term in column.lower() for term in financial_terms):
                if pd.api.types.is_numeric_dtype(df[column]):
                    df.loc[df[column] < 0, column] = pd.NA

        cleaned[table_name] = df

    return cleaned


def create_derived_columns(data):
    """Create derived fields only when their source columns are available."""
    cleaned = {}

    for table_name, df in data.items():
        df = df.copy()

        if table_name == "claims" and {
            "claim_amount", "approved_amount"
        }.issubset(df.columns):
            df["unapproved_amount"] = (
                df["claim_amount"] - df["approved_amount"]
            )

        cleaned[table_name] = df

    return cleaned


def clean_data(data):
    """Run the cleaning steps in sequence."""
    data = handle_missing_values(data)
    data = remove_duplicates(data)
    data = clean_text_columns(data)
    data = clean_date_columns(data)
    data = validate_numeric_columns(data)
    data = validate_business_rules(data)
    data = create_derived_columns(data)

    return data


def save_cleaned_data(data, output_dir):
    """Save cleaned tables without changing the raw source files."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for table_name, df in data.items():
        output_path = output_dir / f"{table_name}_cleaned.csv"
        df.to_csv(output_path, index=False)