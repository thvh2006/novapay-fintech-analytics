# Exploratory Data Analysis — Decision Notes

## Executive summary

The dataset is suitable for an account-behaviour and banking-operations dashboard, but several naive fintech metrics would be misleading. All 4,500 accounts receive a posting on their opening date, and recurring system postings make raw monthly activity appear close to 100%. V1 therefore separates ledger activity from a narrower engagement proxy.

## Validated scope

- Transaction period: 1993-01-01 to 1998-12-31.
- Accounts: 4,500.
- Clients: 5,369.
- Transactions: 1,056,320.
- Loans: 682.
- Transaction value recorded: approximately CZK 6.258 billion.
- All primary keys are complete and unique; every transaction maps to an account.

## Key findings

### 1. Raw first transaction cannot represent activation

Every account has a transaction on its opening date, typically an opening cash deposit. A naive activation calculation would therefore report 100% immediate activation.

**Decision:** define activation as the first operation that is neither a system/unspecified posting nor a cash deposit.

Under this definition:

- 2,268 of 4,500 accounts activate within 30 days: **50.4%**.
- 3,785 activate within 60 days: **84.1%**.
- 4,219 activate within 90 days: **93.8%**.
- Median time to activation is **30 days**.

### 2. Raw active-account retention is inflated

Interest and statement-fee postings can keep an account “active” even when there is no meaningful customer behaviour. Exact-month cohort activity also rises between months 1 and 3, so it should not be labelled survival retention.

**Decision:** report `posting_accounts` and `engaged_accounts` separately. Name the cohort view **cohort engagement**, not retention.

### 3. Scale grew strongly, but dataset coverage drives part of the trend

- Maximum monthly posting accounts rose from 1,138 in 1993 to 4,480 in 1998.
- Annual transaction count rose from 28,205 to 322,277.
- Engaged transaction count rose from 15,455 to 222,696.
- No new account openings appear in 1998, indicating a source-boundary effect rather than a real acquisition collapse.

**Decision:** use 1993–1997 for acquisition/cohort comparisons. Use 1998 for portfolio activity, but not for conclusions about new-account growth.

### 4. Portfolio cash flow remained positive

Total credit value exceeds total debit value in every observed year. Annual net flow ranged from approximately CZK 18.3 million to CZK 49.7 million.

**Decision:** show credit, debit, and net flow together. Do not describe net flow as revenue or profit.

### 5. A small but material risk segment is visible

- 39 accounts end the dataset with a negative latest balance.
- 76 of 682 loans are observed problem loans: **11.1%**.
- Problem-loan principal totals approximately **CZK 15.58 million**.

**Decision:** include a compact risk panel in the executive dashboard, then reserve detailed credit-risk modelling for a later module.

## Recommended dashboard pages

### Executive overview

- Posting accounts and engaged accounts.
- Transaction count and engaged transaction count.
- Credit value, debit value, and net flow.
- Average ending balance and negative-balance accounts.

### Acquisition and engagement

- New accounts by month through 1997.
- 30/60/90-day activation.
- Median days to activation.
- Cohort engagement heatmap.

### Transaction operations

- Operation and category mix.
- Monthly transaction count/value.
- Credits versus debits.
- Regional and account-level drill-down.

### Risk snapshot

- Loan status composition.
- Problem-loan count/value.
- Negative-balance accounts.
- Loan portfolio by region and account tenure.

## Next analytical questions

1. Which customer/account attributes are associated with faster activation?
2. Which regions contribute high balances versus high problem-loan exposure?
3. Are cardholders more engaged after controlling for account tenure?
4. Which operation types drive the increase in transaction volume?

