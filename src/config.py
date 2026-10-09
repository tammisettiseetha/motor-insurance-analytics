
from pathlib import Path

# Main project folder
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
RAW_DATA_DIR = BASE_DIR / "data" / "raw"
CLEANED_DATA_DIR = BASE_DIR / "data" / "cleaned"

# Individual dataset paths
CUSTOMERS_FILE = RAW_DATA_DIR / "customers.csv"
VEHICLES_FILE = RAW_DATA_DIR / "vehicles.csv"
POLICIES_FILE = RAW_DATA_DIR / "policies.csv"
CLAIMS_FILE = RAW_DATA_DIR / "claims.csv"
PAYMENTS_FILE = RAW_DATA_DIR / "payments.csv"