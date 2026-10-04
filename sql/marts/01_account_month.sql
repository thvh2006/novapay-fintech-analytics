CREATE OR REPLACE TABLE mart_account_month AS
WITH monthly_flows AS (
    SELECT
        account_id,
        date_trunc('month', transaction_date)::DATE AS activity_month,
        count(*) AS transaction_count,
        count(*) FILTER (
            WHERE operation_type NOT IN ('unspecified', 'cash_deposit')
        ) AS engaged_transaction_count,
        count(*) FILTER (WHERE transaction_direction = 'credit') AS credit_count,
        count(*) FILTER (WHERE transaction_direction = 'debit') AS debit_count,
        sum(amount_czk) FILTER (WHERE transaction_direction = 'credit') AS credit_value_czk,
        sum(amount_czk) FILTER (WHERE transaction_direction = 'debit') AS debit_value_czk,
        avg(amount_czk) AS average_transaction_value_czk
    FROM transactions
    GROUP BY account_id, activity_month
),
month_end_balance AS (
    SELECT
        account_id,
        date_trunc('month', transaction_date)::DATE AS activity_month,
        balance_czk AS ending_balance_czk
    FROM transactions
    QUALIFY row_number() OVER (
        PARTITION BY account_id, date_trunc('month', transaction_date)
        ORDER BY transaction_date DESC, transaction_id DESC
    ) = 1
)
SELECT
    f.account_id,
    f.activity_month,
    f.transaction_count,
    f.engaged_transaction_count,
    f.credit_count,
    f.debit_count,
    coalesce(f.credit_value_czk, 0) AS credit_value_czk,
    coalesce(f.debit_value_czk, 0) AS debit_value_czk,
    coalesce(f.credit_value_czk, 0) - coalesce(f.debit_value_czk, 0) AS net_flow_czk,
    f.average_transaction_value_czk,
    b.ending_balance_czk
FROM monthly_flows f
JOIN month_end_balance b USING (account_id, activity_month);
