from pathlib import Path

from src.data_loader import load_all_data
from src.validation import validate_all_tables
from src.data_cleaner import clean_data, save_cleaned_data
from src.logger import log_pipeline_step, log_error


BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"


def run_pipeline():
    """Load, validate, clean, and save insurance datasets."""
    try:
        log_pipeline_step("Pipeline started.")

        # 1. Load raw datasets
        data = load_all_data(RAW_DIR)
        log_pipeline_step("Raw datasets loaded.")

        # 2. Validate datasets
        errors = validate_all_tables(data)

        if errors:
            for error in errors:
                log_error(error)

            raise ValueError(
                "Validation failed. Review logs/pipeline.log for details."
            )

        log_pipeline_step("Validation completed successfully.")

        # 3. Clean datasets
        cleaned_data = clean_data(data)
        log_pipeline_step("Data cleaning completed.")

        # 4. Save cleaned datasets
        save_cleaned_data(cleaned_data, CLEANED_DIR)
        log_pipeline_step("Cleaned datasets saved.")

        print("Pipeline completed successfully.")
        print(f"Cleaned files saved to: {CLEANED_DIR}")

        for name, df in cleaned_data.items():
            print(f"{name}: {df.shape[0]} rows, {df.shape[1]} columns")

        return cleaned_data

    except Exception as error:
        log_error(f"Pipeline failed: {error}")
        raise


if __name__ == "__main__":
    run_pipeline()