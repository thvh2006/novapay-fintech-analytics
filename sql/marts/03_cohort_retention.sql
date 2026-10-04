DROP TABLE IF EXISTS mart_cohort_retention;

CREATE OR REPLACE TABLE mart_cohort_engagement AS
WITH account_cohorts AS (
    SELECT
        account_id,
        date_trunc('month', opened_date)::DATE AS cohort_month
    FROM accounts
),
cohort_sizes AS (
    SELECT cohort_month, count(*) AS cohort_size
    FROM account_cohorts
    GROUP BY cohort_month
),
cohort_activity AS (
    SELECT
        c.cohort_month,
        date_diff('month', c.cohort_month, am.activity_month) AS months_since_open,
        count(DISTINCT am.account_id) AS retained_accounts
    FROM account_cohorts c
    JOIN mart_account_month am USING (account_id)
    WHERE am.activity_month >= c.cohort_month
      AND am.engaged_transaction_count > 0
    GROUP BY c.cohort_month, months_since_open
)
SELECT
    ca.cohort_month,
    ca.months_since_open,
    cs.cohort_size,
    ca.retained_accounts AS engaged_accounts,
    round(ca.retained_accounts::DOUBLE / cs.cohort_size, 4) AS engagement_rate
FROM cohort_activity ca
JOIN cohort_sizes cs USING (cohort_month)
ORDER BY cohort_month, months_since_open;

