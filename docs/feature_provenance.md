# Feature provenance and decision-time policy

This register explains where portfolio-facing features come from and what was known at the decision point. The machine-readable source is [`reports/feature_provenance.csv`](../reports/feature_provenance.csv).

| Feature | Family | Raw source | Transformation | Cutoff | Fit scope | Role | Main risk |
|---|---|---|---|---|---|---|---|
| loan_amount_czk | loan terms | loans.loan_amount_czk | Raw origination amount | loan_date | none | model | low |
| duration_months | loan terms | loans.duration_months | Raw term | loan_date | none | model | low |
| monthly_payment_czk | loan terms | loans.monthly_payment_czk | Raw scheduled payment | loan_date | none | model | low |
| account_tenure_days | relationship | accounts.opened_date | loan_date - opened_date | loan_date | none | model | low |
| prior_transaction_count | past behaviour | transactions | Count transactions where transaction_date < loan_date | strictly before loan_date | none | model | low |
| prior_credit_czk | past behaviour | transactions | Sum prior credits | strictly before loan_date | none | model | low |
| prior_debit_czk | past behaviour | transactions | Sum prior debits | strictly before loan_date | none | model | low |
| prior_net_flow_czk | past behaviour | transactions | Prior credits minus prior debits | strictly before loan_date | none | model | low |
| prior_latest_balance_czk | past balance | transactions.balance_czk | Balance from latest strictly prior transaction | strictly before loan_date | none | model | low |
| prior_min_balance_czk | past balance | transactions.balance_czk | Minimum strictly prior balance | strictly before loan_date | none | model | low |
| prior_active_days | past behaviour | transactions.transaction_date | Distinct active days before origination | strictly before loan_date | none | model | low |
| statement_frequency | account | accounts.statement_frequency | Cleaned category | loan_date | development | model | low |
| region_name | district context | districts.region_name | Raw region category | loan_date | development | model | medium |
| average_salary_czk | district context | districts.average_salary_czk | Raw district statistic | loan_date | none | model | medium |
| unemployment_rate_1996 | district context | districts.unemployment_rate_1996 | Raw district statistic | loan_date | none | model | medium |

## Governance rules

1. Outcomes and post-decision events are targets or evaluation evidence, never predictors.
2. Learned bins, imputers, encoders, cutoffs, and feature eligibility are fitted before locked evaluation.
3. Anonymous fields are described by source and statistical behavior; business meanings are not invented.
4. Proxy and fairness risks remain explicit even when protected attributes are unavailable.
5. The notebook is explanatory; reusable code and tests remain the implementation source of truth.
