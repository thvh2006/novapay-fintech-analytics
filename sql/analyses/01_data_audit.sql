-- Confirm source scale, coverage, and the main transaction mix before defining KPIs.

SELECT
    min(transaction_date) AS first_transaction_date,
    max(transaction_date) AS last_transaction_date,
    count(*) AS transaction_count,
    count(DISTINCT account_id) AS transacting_accounts,
    round(sum(amount_czk), 2) AS total_transaction_value_czk
FROM transactions;

SELECT
    operation_type,
    count(*) AS transaction_count,
    round(sum(amount_czk), 2) AS transaction_value_czk,
    round(avg(amount_czk), 2) AS average_transaction_value_czk
FROM transactions
GROUP BY operation_type
ORDER BY transaction_count DESC;

SELECT
    date_trunc('month', transaction_date)::DATE AS transaction_month,
    count(*) AS transaction_count,
    count(DISTINCT account_id) AS active_accounts,
    round(sum(amount_czk), 2) AS transaction_value_czk
FROM transactions
GROUP BY transaction_month
ORDER BY transaction_month;

