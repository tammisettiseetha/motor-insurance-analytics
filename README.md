\# Motor Insurance Claims \& Policy Analytics



\## Project Overview

This project analyzes motor insurance customers, vehicles, policies, claims, and payments to support data-driven business decisions.



\## Objectives

\- Load and validate insurance datasets.

\- Clean data while preserving the original raw files.

\- Analyze policy, claim, customer, vehicle, and premium metrics.

\- Visualize trends and generate business insights.

\- Present findings through a Streamlit dashboard.



\## Project Structure

\- `data/raw/` — Original CSV datasets.

\- `data/cleaned/` — Cleaned datasets.

\- `notebooks/` — Exploratory data analysis.

\- `src/` — Data loading, validation, cleaning, analysis, visualization, insights, and logging.

\- `app/` — Streamlit dashboard.

\- `tests/` — Automated tests.

\- `reports/` — Business report.

\- `run\_pipeline.py` — Main data pipeline.



\## Technologies

Python, Pandas, NumPy, Matplotlib, Seaborn, Streamlit, and Pytest.



\## How to Run

1\. Install the dependencies using `pip install -r requirements.txt`.

2\. Place the five original CSV files in `data/raw/`.

3\. Run the pipeline using `python run\_pipeline.py`.

4\. Run the dashboard using `streamlit run app/streamlit\_app.py`.



\## Data Integrity

Original datasets in `data/raw/` should remain unchanged. Cleaned outputs are saved separately in `data/cleaned/`.

