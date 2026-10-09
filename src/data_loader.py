from pathlib import Path
import pandas as pd


def check_file_exists(file_path):
    """Check whether the specified file exists."""
    path = Path(file_path)

    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")

    return True


def load_table(file_path):
    """Load one CSV file into a Pandas DataFrame."""
    check_file_exists(file_path)

    try:
        return pd.read_csv(file_path)
    except pd.errors.EmptyDataError as error:
        raise ValueError(f"The CSV file is empty: {file_path}") from error
    except pd.errors.ParserError as error:
        raise ValueError(f"Unable to parse CSV file: {file_path}") from error


def load_all_data(data_dir):
    """Load all five raw insurance datasets."""
    data_dir = Path(data_dir)

    file_names = {
        "customers": "customers.csv",
        "policies": "policies.csv",
        "vehicles": "vehicles.csv",
        "claims": "claims.csv",
        "payments": "payments.csv",
    }

    data = {}

    for table_name, file_name in file_names.items():
        file_path = data_dir / file_name
        data[table_name] = load_table(file_path)

    return data