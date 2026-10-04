CREATE OR REPLACE TABLE mart_loan_portfolio AS
SELECT
    l.loan_id,
    l.account_id,
    l.loan_date,
    l.loan_amount_czk,
    l.duration_months,
    l.monthly_payment_czk,
    l.loan_status,
    CASE l.loan_status
        WHEN 'A' THEN 'completed_good'
        WHEN 'B' THEN 'completed_default'
        WHEN 'C' THEN 'active_good'
        WHEN 'D' THEN 'active_delinquent'
    END AS loan_status_label,
    CASE WHEN l.loan_status IN ('B', 'D') THEN true ELSE false END AS observed_problem_loan,
    a.opened_date,
    date_diff('month', a.opened_date, l.loan_date) AS account_tenure_months_at_loan,
    a360.owner_age_at_dataset_end,
    a360.owner_gender,
    a360.region_name,
    a360.card_count,
    a360.latest_balance_czk
FROM loans l
JOIN accounts a USING (account_id)
LEFT JOIN mart_account_360 a360 USING (account_id);

