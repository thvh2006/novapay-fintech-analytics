CREATE OR REPLACE TABLE mart_monthly_performance AS
WITH new_accounts AS (
    SELECT
        date_trunc('month', opened_date)::DATE AS calendar_month,
        count(*) AS new_accounts
    FROM accounts
    GROUP BY calendar_month
)
SELECT
    am.activity_month AS calendar_month,
    count(DISTINCT am.account_id) AS posting_accounts,
    count(DISTINCT am.account_id) FILTER (
        WHERE am.engaged_transaction_count > 0
    ) AS engaged_accounts,
    coalesce(na.new_accounts, 0) AS new_accounts,
    sum(am.transaction_count) AS transaction_count,
    sum(am.engaged_transaction_count) AS engaged_transaction_count,
    sum(am.credit_count) AS credit_count,
    sum(am.debit_count) AS debit_count,
    round(sum(am.credit_value_czk), 2) AS credit_value_czk,
    round(sum(am.debit_value_czk), 2) AS debit_value_czk,
    round(sum(am.net_flow_czk), 2) AS net_flow_czk,
    round(avg(am.average_transaction_value_czk), 2) AS average_account_transaction_value_czk,
    round(avg(am.ending_balance_czk), 2) AS average_ending_balance_czk,
    count(*) FILTER (WHERE am.ending_balance_czk < 0) AS accounts_ending_negative
FROM mart_account_month am
LEFT JOIN new_accounts na ON am.activity_month = na.calendar_month
GROUP BY am.activity_month, na.new_accounts
ORDER BY calendar_month;
