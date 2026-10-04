CREATE OR REPLACE TABLE mart_customer_segments AS
WITH meaningful_activity AS (
    SELECT
        account_id,
        count(*) FILTER (
            WHERE operation_type NOT IN ('unspecified', 'cash_deposit')
        ) AS engaged_transaction_count,
        count(DISTINCT date_trunc('month', transaction_date)) FILTER (
            WHERE operation_type NOT IN ('unspecified', 'cash_deposit')
        ) AS engaged_months,
        max(transaction_date) FILTER (
            WHERE operation_type NOT IN ('unspecified', 'cash_deposit')
        ) AS last_engaged_date,
        sum(amount_czk) FILTER (
            WHERE transaction_direction = 'credit'
              AND operation_type NOT IN ('unspecified', 'cash_deposit')
        ) AS engaged_credit_value_czk,
        sum(amount_czk) FILTER (
            WHERE transaction_direction = 'debit'
              AND operation_type NOT IN ('unspecified', 'cash_deposit')
        ) AS engaged_debit_value_czk
    FROM transactions
    GROUP BY account_id
),
account_features AS (
    SELECT
        a360.*,
        activation.days_to_activation,
        activity.engaged_transaction_count,
        activity.engaged_months,
        activity.last_engaged_date,
        date_diff('day', activity.last_engaged_date, DATE '1998-12-31') AS engagement_recency_days,
        round(activity.engaged_credit_value_czk, 2) AS engaged_credit_value_czk,
        round(activity.engaged_debit_value_czk, 2) AS engaged_debit_value_czk,
        round(
            activity.engaged_transaction_count
            / nullif(activity.engaged_months, 0),
            2
        ) AS average_engaged_transactions_per_month
    FROM mart_account_360 a360
    JOIN mart_account_activation activation USING (account_id)
    JOIN meaningful_activity activity USING (account_id)
),
thresholds AS (
    SELECT
        quantile_cont(engaged_transaction_count, 0.50) AS median_engaged_transactions,
        quantile_cont(engaged_transaction_count, 0.75) AS p75_engaged_transactions,
        quantile_cont(lifetime_credit_value_czk, 0.75) AS p75_lifetime_credit,
        quantile_cont(latest_balance_czk, 0.75) AS p75_latest_balance
    FROM account_features
),
segmented AS (
    SELECT
        features.*,
        CASE
            WHEN latest_balance_czk < 0 OR latest_loan_status IN ('B', 'D')
                THEN 'Risk watch'
            WHEN lifetime_credit_value_czk >= p75_lifetime_credit
                AND latest_balance_czk >= p75_latest_balance
                AND engaged_transaction_count >= p75_engaged_transactions
                THEN 'High-value relationship'
            WHEN latest_loan_status IN ('A', 'C')
                THEN 'Healthy borrower'
            WHEN card_count > 0
                AND engaged_transaction_count >= median_engaged_transactions
                THEN 'Card-led engaged'
            WHEN engaged_transaction_count >= median_engaged_transactions
                THEN 'Core transactional'
            ELSE 'Light relationship'
        END AS customer_segment
    FROM account_features features
    CROSS JOIN thresholds
)
SELECT
    *,
    CASE customer_segment
        WHEN 'Risk watch'
            THEN 'Negative balance or observed problem-loan status'
        WHEN 'High-value relationship'
            THEN 'Top-quartile credit value ending balance and engagement'
        WHEN 'Healthy borrower'
            THEN 'Completed-good or active-good loan relationship'
        WHEN 'Card-led engaged'
            THEN 'Cardholder with above-median engagement'
        WHEN 'Core transactional'
            THEN 'Above-median engagement without a card or loan priority flag'
        ELSE 'Below-median engagement and no higher-priority relationship flag'
    END AS segment_definition,
    CASE customer_segment
        WHEN 'Risk watch'
            THEN 'Prioritise review repayment support and balance alerts'
        WHEN 'High-value relationship'
            THEN 'Protect service quality and test premium relationship benefits'
        WHEN 'Healthy borrower'
            THEN 'Offer relevant credit servicing and repayment reminders'
        WHEN 'Card-led engaged'
            THEN 'Deepen card usage with merchant and recurring-payment offers'
        WHEN 'Core transactional'
            THEN 'Promote card adoption and additional account features'
        ELSE 'Use onboarding education and low-friction activation nudges'
    END AS recommended_action
FROM segmented;

CREATE OR REPLACE TABLE mart_segment_summary AS
SELECT
    customer_segment,
    count(*) AS accounts,
    round(count(*) / sum(count(*)) OVER (), 4) AS portfolio_share,
    round(avg(days_to_activation), 1) AS average_days_to_activation,
    round(avg(engaged_transaction_count), 1) AS average_engaged_transactions,
    round(avg(latest_balance_czk), 2) AS average_latest_balance_czk,
    count(*) FILTER (WHERE latest_balance_czk < 0) AS negative_balance_accounts,
    count(*) FILTER (WHERE latest_loan_status IN ('B', 'D')) AS problem_loan_accounts,
    any_value(segment_definition) AS segment_definition,
    any_value(recommended_action) AS recommended_action
FROM mart_customer_segments
GROUP BY customer_segment
ORDER BY accounts DESC;
