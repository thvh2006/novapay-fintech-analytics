CREATE OR REPLACE TABLE mart_account_activation AS
WITH first_meaningful_activity AS (
    SELECT
        account_id,
        min(transaction_date) AS first_meaningful_activity_date
    FROM transactions
    WHERE operation_type NOT IN ('unspecified', 'cash_deposit')
    GROUP BY account_id
)
SELECT
    a.account_id,
    a.opened_date,
    f.first_meaningful_activity_date,
    date_diff('day', a.opened_date, f.first_meaningful_activity_date) AS days_to_activation,
    date_diff('day', a.opened_date, f.first_meaningful_activity_date) <= 30 AS activated_within_30d,
    date_diff('day', a.opened_date, f.first_meaningful_activity_date) <= 60 AS activated_within_60d,
    date_diff('day', a.opened_date, f.first_meaningful_activity_date) <= 90 AS activated_within_90d
FROM accounts a
LEFT JOIN first_meaningful_activity f USING (account_id);

