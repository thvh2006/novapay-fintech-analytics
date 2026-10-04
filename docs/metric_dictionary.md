# Metric Dictionary — V1

The Berka source is a traditional banking dataset. V1 therefore uses account and cash-flow metrics rather than pretending the records describe a modern digital wallet.

| Metric | Business definition | Grain/window | Important caveat |
|---|---|---|---|
| Posting accounts | Distinct accounts with any ledger posting in the month | Account-month | Includes automated interest and fee postings |
| Engaged accounts | Distinct accounts with at least one transaction whose operation is not `unspecified` or `cash_deposit` | Account-month | Includes recurring transfers; this is an engagement proxy, not app usage |
| New accounts | Accounts opened during the calendar month | Month | No new accounts appear in 1998 because of source coverage |
| 30-day activation | Share of new accounts reaching their first non-system, non-opening-deposit activity within 30 days | Opening cohort | Historical bank-account activation proxy |
| Median days to activation | Median days from account opening to first non-system, non-opening-deposit activity | Opening cohort | Opening cash deposit is excluded |
| Transaction count | Number of ledger transactions | Month | Includes system-generated postings |
| Engaged transaction count | Transactions excluding `unspecified` operations and cash deposits | Month | A behavioural subset of total transaction count |
| Credit value | Total value of transactions recorded as credits | Month, CZK | Flow, not revenue |
| Debit value | Total value of transactions recorded as debits | Month, CZK | Flow, not cost |
| Net flow | Credit value minus debit value | Month, CZK | Not profit and not change in total bank assets |
| Average ending balance | Average latest recorded account balance in the month | Account-month, CZK | Only accounts with a posting that month are included |
| Negative-balance accounts | Accounts whose latest balance in the month is below zero | Account-month | Operational/risk monitoring indicator |
| Cohort engagement rate | Share of an opening cohort with meaningful activity in exact month N after opening | Cohort-month | Can rise or fall; it is not survival retention |
| Observed problem-loan rate | Loans with status B or D divided by all recorded loans | Loan portfolio | Mixes completed default and active delinquency; not an application approval rate |
| Customer segment | One mutually exclusive relationship group assigned by ordered risk, value, product, and engagement rules | Account | Descriptive targeting framework, not a predictive or causal model |

## Metric ownership in the case study

- Growth/Product: new accounts, activation, cohort engagement.
- Operations: transaction count, engaged accounts, transaction mix.
- Finance/Treasury: credit value, debit value, net flow, ending balance.
- Risk: negative-balance accounts and observed problem loans.
