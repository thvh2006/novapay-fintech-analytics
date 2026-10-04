CREATE OR REPLACE TABLE mart_account_360 AS
WITH owner AS (
    SELECT
        d.account_id,
        c.client_id AS owner_client_id,
        c.gender AS owner_gender,
        c.birth_date AS owner_birth_date,
        c.district_id
    FROM dispositions d
    JOIN clients c USING (client_id)
    WHERE d.disposition_type = 'owner'
),
transaction_summary AS (
    SELECT
        account_id,
        min(transaction_date) AS first_transaction_date,
        max(transaction_date) AS last_transaction_date,
        count(*) AS lifetime_transaction_count,
        sum(amount_czk) FILTER (WHERE transaction_direction = 'credit') AS lifetime_credit_value_czk,
        sum(amount_czk) FILTER (WHERE transaction_direction = 'debit') AS lifetime_debit_value_czk,
        count(DISTINCT date_trunc('month', transaction_date)) AS active_months
    FROM transactions
    GROUP BY account_id
),
last_balance AS (
    SELECT account_id, balance_czk AS latest_balance_czk
    FROM transactions
    QUALIFY row_number() OVER (
        PARTITION BY account_id ORDER BY transaction_date DESC, transaction_id DESC
    ) = 1
),
card_summary AS (
    SELECT
        d.account_id,
        count(*) AS card_count,
        max_by(c.card_type, c.issued_date) AS latest_card_type
    FROM cards c
    JOIN dispositions d USING (disposition_id)
    GROUP BY d.account_id
),
loan_summary AS (
    SELECT
        account_id,
        count(*) AS loan_count,
        sum(loan_amount_czk) AS total_loan_amount_czk,
        max_by(loan_status, loan_date) AS latest_loan_status
    FROM loans
    GROUP BY account_id
)
SELECT
    a.account_id,
    o.owner_client_id,
    o.owner_gender,
    o.owner_birth_date,
    date_diff('year', o.owner_birth_date, DATE '1998-12-31') AS owner_age_at_dataset_end,
    a.opened_date,
    a.statement_frequency,
    dist.district_name,
    dist.region_name,
    ts.first_transaction_date,
    ts.last_transaction_date,
    ts.lifetime_transaction_count,
    round(ts.lifetime_credit_value_czk, 2) AS lifetime_credit_value_czk,
    round(ts.lifetime_debit_value_czk, 2) AS lifetime_debit_value_czk,
    ts.active_months,
    lb.latest_balance_czk,
    coalesce(cs.card_count, 0) AS card_count,
    cs.latest_card_type,
    coalesce(ls.loan_count, 0) AS loan_count,
    coalesce(ls.total_loan_amount_czk, 0) AS total_loan_amount_czk,
    ls.latest_loan_status
FROM accounts a
JOIN owner o USING (account_id)
LEFT JOIN districts dist ON dist.district_id = o.district_id
LEFT JOIN transaction_summary ts USING (account_id)
LEFT JOIN last_balance lb USING (account_id)
LEFT JOIN card_summary cs USING (account_id)
LEFT JOIN loan_summary ls USING (account_id);
