from pathlib import Path
import sys

# Make the project root available for imports.
BASE_DIR = Path(__file__).resolve().parent.parent

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

from src.insurance_analysis import (
    calculate_all_kpis,
    analyze_customer_claims,
    analyze_customer_premium,
    analyze_vehicle_claims,
    analyze_vehicle_risk_patterns,
    analyze_vehicle_type,
)

from src.insights import (
    generate_portfolio_insights,
    generate_claim_insights,
    generate_premium_insights,
    generate_customer_insights,
    generate_vehicle_insights,
    generate_risk_patterns,
    generate_business_recommendations,
)

from src.visualization import (
    plot_policy_status,
    plot_policy_type_distribution,
    plot_premium_by_policy_type,
    plot_monthly_claims,
    plot_claim_status,
    plot_claim_type_distribution,
    plot_claim_amount_distribution,
    plot_claim_amount_by_vehicle_type,
    plot_claims_by_region,
    plot_claim_severity_by_region,
    plot_average_settlement_time,
    plot_claim_to_premium_by_policy_type,
    plot_vehicle_age_vs_claim_amount,
    plot_customer_age_vs_claim_amount,
    plot_vehicle_type_claim_performance,
    plot_damage_severity_distribution,
    plot_payment_status,
    plot_monthly_premium_trend,
)


RAW_DIR = BASE_DIR / "data" / "raw"
CLEANED_DIR = BASE_DIR / "data" / "cleaned"

TABLES = [
    "customers",
    "policies",
    "vehicles",
    "claims",
    "payments",
]


# ============================================================
# DATA LOADING
# ============================================================

def load_dashboard_data():
    """Load cleaned insurance datasets, falling back to raw CSVs."""
    data = {}

    for name in TABLES:
        cleaned_path = CLEANED_DIR / f"{name}_cleaned.csv"
        raw_path = RAW_DIR / f"{name}.csv"

        file_path = (
            cleaned_path if cleaned_path.exists() else raw_path
        )

        if not file_path.exists():
            raise FileNotFoundError(
                f"Dataset not found: {file_path}"
            )

        data[name] = pd.read_csv(file_path)

    return data


# ============================================================
# SIDEBAR FILTERS
# ============================================================

def _category_values(df, column):
    """Return filter categories, including missing values."""
    if column not in df.columns:
        return []

    values = (
        df[column]
        .astype("string")
        .str.strip()
        .fillna("Unknown")
        .replace("", "Unknown")
    )

    return sorted(values.unique().tolist())
def _apply_category_filter(df, column, selected_values):
    """Apply a category filter while preserving selectable missing values."""
    if column not in df.columns or selected_values is None:
        return df.copy()

    values = (
        df[column]
        .astype("string")
        .str.strip()
        .fillna("Unknown")
        .replace("", "Unknown")
    )

    if not selected_values:
        return df.iloc[0:0].copy()

    return df[values.isin(selected_values)].copy()


def show_sidebar_filters(data):
    """Apply sidebar filters to connected datasets."""
    st.sidebar.header("Dashboard Filters")

    original = {
        name: df.copy()
        for name, df in data.items()
    }

    customers = original["customers"]
    vehicles = original["vehicles"]
    policies = original["policies"]
    claims = original["claims"]
    payments = original["payments"]

    # Customer location filters
    selected_states = st.sidebar.multiselect(
        "State",
        _category_values(customers, "state"),
        default=_category_values(customers, "state"),
    )

    selected_cities = st.sidebar.multiselect(
        "City",
        _category_values(customers, "city"),
        default=_category_values(customers, "city"),
    )

    filtered_customers = _apply_category_filter(
        customers, "state", selected_states
    )
    filtered_customers = _apply_category_filter(
        filtered_customers, "city", selected_cities
    )

    customer_ids = set(
        filtered_customers["customer_id"].dropna()
    )

    # Vehicle filters
    selected_vehicle_types = st.sidebar.multiselect(
        "Vehicle Type",
        _category_values(vehicles, "vehicle_type"),
        default=_category_values(vehicles, "vehicle_type"),
    )

    selected_vehicle_makes = st.sidebar.multiselect(
        "Vehicle Make",
        _category_values(vehicles, "vehicle_make"),
        default=_category_values(vehicles, "vehicle_make"),
    )

    filtered_vehicles = _apply_category_filter(
        vehicles, "vehicle_type", selected_vehicle_types
    )
    filtered_vehicles = _apply_category_filter(
        filtered_vehicles, "vehicle_make", selected_vehicle_makes
    )

    filtered_vehicles = filtered_vehicles[
        filtered_vehicles["customer_id"].isin(customer_ids)
    ].copy()

    vehicle_ids = set(
        filtered_vehicles["vehicle_id"].dropna()
    )

    # Policy filters
    selected_policy_types = st.sidebar.multiselect(
        "Policy Type",
        _category_values(policies, "policy_type"),
        default=_category_values(policies, "policy_type"),
    )

    selected_policy_statuses = st.sidebar.multiselect(
        "Policy Status",
        _category_values(policies, "policy_status"),
        default=_category_values(policies, "policy_status"),
    )

    filtered_policies = _apply_category_filter(
        policies, "policy_type", selected_policy_types
    )
    filtered_policies = _apply_category_filter(
        filtered_policies, "policy_status", selected_policy_statuses
    )

    filtered_policies = filtered_policies[
        filtered_policies["customer_id"].isin(customer_ids)
        & filtered_policies["vehicle_id"].isin(vehicle_ids)
    ].copy()

    policy_ids = set(
        filtered_policies["policy_id"].dropna()
    )

    # Claim date filter
    selected_claims = claims[
        claims["policy_id"].isin(policy_ids)
    ].copy()

    if not selected_claims.empty:
        claim_dates = pd.to_datetime(
            selected_claims["claim_date"], errors="coerce"
        ).dropna()

        if not claim_dates.empty:
            date_range = st.sidebar.date_input(
                "Claim Date Range",
                value=(
                    claim_dates.min().date(),
                    claim_dates.max().date(),
                ),
            )

            if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
                start_date = pd.Timestamp(date_range[0])
                end_date = (
                    pd.Timestamp(date_range[1])
                    + pd.Timedelta(days=1)
                )

                parsed_dates = pd.to_datetime(
                    selected_claims["claim_date"],
                    errors="coerce",
                )

                selected_claims = selected_claims[
                    parsed_dates.ge(start_date)
                    & parsed_dates.lt(end_date)
                ].copy()

    # Claim filters
    selected_claim_statuses = st.sidebar.multiselect(
        "Claim Status",
        _category_values(claims, "claim_status"),
        default=_category_values(claims, "claim_status"),
    )

    selected_claim_types = st.sidebar.multiselect(
        "Claim Type",
        _category_values(claims, "claim_type"),
        default=_category_values(claims, "claim_type"),
    )

    selected_severities = st.sidebar.multiselect(
        "Damage Severity",
        _category_values(claims, "damage_severity"),
        default=_category_values(claims, "damage_severity"),
    )

    selected_claims = _apply_category_filter(
        selected_claims,
        "claim_status",
        selected_claim_statuses,
    )

    selected_claims = _apply_category_filter(
        selected_claims,
        "claim_type",
        selected_claim_types,
    )

    selected_claims = _apply_category_filter(
        selected_claims,
        "damage_severity",
        selected_severities,
    )

    # Match payments to the selected claim and policy IDs.
    claim_ids = set(
        selected_claims["claim_id"].dropna()
    )

    selected_payments = payments[
        payments["policy_id"].isin(policy_ids)
        & payments["claim_id"].isin(claim_ids)
    ].copy()

    # Keep customers and vehicles relevant to the selected policies.
    selected_customer_ids = (
        set(filtered_policies["customer_id"].dropna())
        | set(selected_claims["customer_id"].dropna())
    )

    selected_vehicle_ids = set(
        filtered_policies["vehicle_id"].dropna()
    )

    selected_customers = filtered_customers[
        filtered_customers["customer_id"].isin(
            selected_customer_ids
        )
    ].copy()

    selected_vehicles = filtered_vehicles[
        filtered_vehicles["vehicle_id"].isin(
            selected_vehicle_ids
        )
    ].copy()

    return {
        "customers": selected_customers,
        "vehicles": selected_vehicles,
        "policies": filtered_policies,
        "claims": selected_claims,
        "payments": selected_payments,
    }


# ============================================================
# COMMON DISPLAY HELPERS
# ============================================================

def _show_chart(chart_function, *args):
    """Display a returned Matplotlib figure."""
    fig = None

    try:
        fig = chart_function(*args)
        st.pyplot(fig)

    except (ValueError, KeyError, TypeError) as error:
        st.info(
            f"This chart is unavailable for the current data selection: "
            f"{error}"
        )

    finally:
        if fig is not None:
            plt.close(fig)


def _format_kpi(value, kind="number"):
    """Format KPI values for display."""
    if value is None or pd.isna(value):
        return "N/A"

    if kind == "money":
        return f"{value:,.2f}"

    if kind == "rate":
        return f"{value:.2f}%"

    if kind == "ratio":
        return f"{value:.2%}"

    if kind == "days":
        return f"{value:.1f} days"

    return f"{value:,.0f}"


def _calculate_kpis(data):
    """Calculate KPIs and show a helpful message if something fails."""
    try:
        return calculate_all_kpis(data)

    except (KeyError, ValueError, TypeError) as error:
        st.error(f"Unable to calculate KPIs: {error}")
        return {}


def _show_kpi_row(kpis, labels):
    """Display a row of KPI cards."""
    columns = st.columns(len(labels))

    for column, (label, kind) in zip(columns, labels):
        column.metric(
            label,
            _format_kpi(kpis.get(label), kind),
        )


# ============================================================
# EXECUTIVE OVERVIEW
# ============================================================

def show_overview(data):
    """Display the executive overview and main KPIs."""
    st.header("Executive Overview")

    kpis = _calculate_kpis(data)

    if kpis:
        _show_kpi_row(
            kpis,
            [
                ("Total Policies", "number"),
                ("Active Policies", "number"),
                ("Total Premium", "money"),
                ("Total Claims", "number"),
            ],
        )

        _show_kpi_row(
            kpis,
            [
                ("Total Claim Amount", "money"),
                ("Claim Approval Rate (%)", "rate"),
                ("Average Settlement Days", "days"),
            ],
        )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Policy Status")
        _show_chart(plot_policy_status, data["policies"])

    with col2:
        st.subheader("Claim Status")
        _show_chart(plot_claim_status, data["claims"])


# ============================================================
# POLICY ANALYSIS
# ============================================================

def show_policy_analysis(data):
    """Show policy activity, type distribution, and premium trends."""
    st.header("Policy Analysis")

    col1, col2 = st.columns(2)

    with col1:
        _show_chart(plot_policy_status, data["policies"])
        _show_chart(
            plot_policy_type_distribution,
            data["policies"],
        )

    with col2:
        _show_chart(
            plot_premium_by_policy_type,
            data["policies"],
        )
        _show_chart(
            plot_monthly_premium_trend,
            data["policies"],
        )

    st.subheader("Policy Records")
    st.dataframe(
        data["policies"].head(100),
        use_container_width=True,
    )


# ============================================================
# CLAIM ANALYSIS
# ============================================================

def show_claim_analysis(data):
    """Show claim volume, status, severity, and settlement patterns."""
    st.header("Claims Analysis")

    col1, col2 = st.columns(2)

    with col1:
        _show_chart(plot_claim_status, data["claims"])
        _show_chart(
            plot_claim_type_distribution,
            data["claims"],
        )
        _show_chart(
            plot_claim_amount_distribution,
            data["claims"],
        )
        _show_chart(
            plot_damage_severity_distribution,
            data["claims"],
        )

    with col2:
        _show_chart(
            plot_monthly_claims,
            data["claims"],
        )
        _show_chart(
            plot_claim_amount_by_vehicle_type,
            data["claims"],
            data["policies"],
            data["vehicles"],
        )
        _show_chart(
            plot_claims_by_region,
            data["claims"],
            data["customers"],
        )
        _show_chart(
            plot_claim_severity_by_region,
            data["claims"],
            data["customers"],
        )
        _show_chart(
            plot_average_settlement_time,
            data["claims"],
        )

    st.subheader("Claim Records")
    st.dataframe(
        data["claims"].head(100),
        use_container_width=True,
    )


# ============================================================
# CUSTOMER ANALYSIS
# ============================================================

def show_customer_analysis(data):
    """Show customer demographics, claim activity, and premium behavior."""
    st.header("Customer Analysis")

    _show_chart(
        plot_customer_age_vs_claim_amount,
        data["claims"],
        data["customers"],
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Customer Claim Summary")

        try:
            customer_claims = analyze_customer_claims(data)

            st.dataframe(
                customer_claims.head(100),
                use_container_width=True,
            )

        except (KeyError, ValueError, TypeError) as error:
            st.info(f"Customer claim summary unavailable: {error}")

    with col2:
        st.subheader("Customer Premium Summary")

        try:
            customer_premium = analyze_customer_premium(data)

            st.dataframe(
                customer_premium.head(100),
                use_container_width=True,
            )

        except (KeyError, ValueError, TypeError) as error:
            st.info(f"Customer premium summary unavailable: {error}")

    st.subheader("Customer Records")
    st.dataframe(
        data["customers"].head(100),
        use_container_width=True,
    )


# ============================================================
# VEHICLE ANALYSIS
# ============================================================

def show_vehicle_analysis(data):
    """Show vehicle characteristics and associated claim patterns."""
    st.header("Vehicle Analysis")

    _show_chart(
        plot_vehicle_age_vs_claim_amount,
        data["claims"],
        data["policies"],
        data["vehicles"],
    )

    _show_chart(
        plot_vehicle_type_claim_performance,
        data["claims"],
        data["policies"],
        data["vehicles"],
    )

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Vehicle Claim Summary")

        try:
            st.dataframe(
                analyze_vehicle_claims(data).head(100),
                use_container_width=True,
            )

        except (KeyError, ValueError, TypeError) as error:
            st.info(f"Vehicle claim summary unavailable: {error}")

    with col2:
        st.subheader("Vehicle-Type Summary")

        try:
            st.dataframe(
                analyze_vehicle_type(data),
                use_container_width=True,
            )

        except (KeyError, ValueError, TypeError) as error:
            st.info(f"Vehicle-type summary unavailable: {error}")

    st.subheader("Vehicle Risk Patterns")

    try:
        risk = analyze_vehicle_risk_patterns(data)

        st.dataframe(
            risk.head(100),
            use_container_width=True,
        )

    except (KeyError, ValueError, TypeError) as error:
        st.info(f"Vehicle risk analysis unavailable: {error}")


# ============================================================
# PREMIUM AND RISK ANALYSIS
# ============================================================

def show_premium_analysis(data):
    """Show premium, coverage, and claim-to-premium measures."""
    st.header("Premium & Risk Analysis")

    kpis = _calculate_kpis(data)

    if kpis:
        _show_kpi_row(
            kpis,
            [
                ("Total Premium", "money"),
                ("Average Premium", "money"),
                ("Average Coverage", "money"),
                ("Total Claim Amount", "money"),
            ],
        )

        _show_kpi_row(
            kpis,
            [
                ("Claim-to-Premium Ratio", "ratio"),
                ("Claim-to-Coverage Ratio", "ratio"),
                ("Paid Claim Ratio", "ratio"),
            ],
        )

    col1, col2 = st.columns(2)

    with col1:
        _show_chart(
            plot_premium_by_policy_type,
            data["policies"],
        )

    with col2:
        _show_chart(
            plot_claim_to_premium_by_policy_type,
            data["claims"],
            data["policies"],
        )

    st.subheader("Payment Status")
    _show_chart(
        plot_payment_status,
        data["payments"],
    )


# ============================================================
# INSIGHTS AND RECOMMENDATIONS
# ============================================================

def show_insights(data):
    """Present the available insights and recommendations."""
    st.header("Insights & Recommendations")

    sections = [
        ("Portfolio Insights", generate_portfolio_insights),
        ("Claim Insights", generate_claim_insights),
        ("Premium Insights", generate_premium_insights),
        ("Customer Insights", generate_customer_insights),
        ("Vehicle Insights", generate_vehicle_insights),
        ("Risk Patterns", generate_risk_patterns),
        (
            "Business Recommendations",
            generate_business_recommendations,
        ),
    ]

    st.caption(
        "Review each finding against the selected data. "
        "Recommendations should be supported by measured evidence."
    )

    for title, function in sections:
        st.subheader(title)

        try:
            results = function(data)

            if not results:
                st.info("No findings are available for this selection.")
                continue

            for result in results:
                st.write(f"- {result}")

        except (KeyError, ValueError, TypeError) as error:
            st.info(f"Section unavailable: {error}")


# ============================================================
# APPLICATION ENTRY POINT
# ============================================================

def main():
    """Run the Streamlit dashboard."""
    st.set_page_config(
        page_title="Motor Insurance Analytics",
        page_icon="🚗",
        layout="wide",
    )

    st.title("Motor Insurance Claims & Policy Analytics")
    st.caption(
        "Policy activity | Premiums | Claims | Customers | Vehicles | Payments"
    )

    try:
        data = load_dashboard_data()

    except (FileNotFoundError, pd.errors.ParserError) as error:
        st.error(f"Unable to load the insurance datasets: {error}")
        st.stop()

    filtered_data = show_sidebar_filters(data)

    pages = {
        "Executive Overview": show_overview,
        "Policy Analysis": show_policy_analysis,
        "Claims Analysis": show_claim_analysis,
        "Customer Analysis": show_customer_analysis,
        "Vehicle Analysis": show_vehicle_analysis,
        "Premium & Risk": show_premium_analysis,
        "Insights & Recommendations": show_insights,
    }

    selected_page = st.sidebar.radio(
        "Navigate to a page",
        list(pages.keys()),
    )

    pages[selected_page](filtered_data)


if __name__ == "__main__":
    main()