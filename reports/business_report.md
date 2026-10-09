\# Motor Insurance Claims \& Policy Analytics



\## 1. Project Overview



This project analyzes motor insurance data across customers, vehicles, policies, claims, and payments. The objective is to organize the data, validate its quality, calculate business KPIs, and present useful findings through visualizations and a Streamlit dashboard.



\## 2. Business Objectives



\* Understand the insurance policy portfolio.

\* Analyze claim volume and claim statuses.

\* Examine premium and payment patterns.

\* Understand customer and vehicle distribution.

\* Identify potential data-quality issues and business risks.

\* Provide evidence-based recommendations.



\## 3. Datasets



The project uses five source datasets:



\* `customers.csv`

\* `vehicles.csv`

\* `policies.csv`

\* `claims.csv`

\* `payments.csv`



The original datasets are stored in `data/raw/`. Cleaned datasets are stored separately in `data/cleaned/`.



\## 4. Data Preparation



The pipeline is designed to check file availability, validate required columns and table relationships, standardize text, handle duplicates, convert applicable data types, and save cleaned outputs.



Missing values are handled according to their meaning. For example, a missing claim approval or settlement date may indicate that a claim is still being processed, so such values should not be automatically replaced.



\## 5. Planned Business Analysis



The analysis will cover:



\* Policy portfolio and policy status.

\* Claim volume, status, and claim amounts.

\* Premium and payment metrics.

\* Customer distribution.

\* Vehicle characteristics.

\* Potential risk patterns and operational improvement opportunities.



\## 6. Visualizations



The dashboard will present suitable charts and KPI summaries for policy, claim, customer, vehicle, and premium analysis.



\## 7. Findings



This section will be completed after the required KPI calculations and exploratory analysis have been run against the actual datasets. No findings or business results are assumed in advance.



\## 8. Recommendations



Recommendations will be based on the measured results. Potential areas for investigation include pending claims, claim processing delays, premium distribution, payment patterns, and data-quality improvements.



\## 9. Testing



Automated tests are maintained in the `tests/` directory. The recorded test result should be updated after the complete test suite is run.



\## 10. Limitations



Conclusions depend on the completeness, accuracy, and definitions of the supplied datasets. Associations in the data should not automatically be interpreted as causal relationships.



\## 11. Conclusion



The project establishes a reproducible workflow for preparing motor insurance data, calculating business metrics, visualizing results, and supporting evidence-based decisions.



