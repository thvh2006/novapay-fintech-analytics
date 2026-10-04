# Data Dictionary

## Source tables

| Table | Grain | Primary key | Source | Key limitation |
|---|---|---|---|---|
| `accounts` | One bank account | `account_id` | Public Berka data | No openings appear in 1998 |
| `clients` | One client | `client_id` | Public Berka data | Demographics are limited and historical |
| `dispositions` | One client-account relationship | `disposition_id` | Public Berka data | Owner and authorised-user relationships only |
| `transactions` | One ledger posting | `transaction_id` | Public Berka data | Includes automated interest and fee postings |
| `loans` | One recorded loan | `loan_id` | Public Berka data | Status is observed outcome, not underwriting decision |
| `cards` | One issued card | `card_id` | Public Berka data | No merchant-level purchase data |
| `standing_orders` | One recurring payment order | `order_id` | Public Berka data | Order execution is not directly identified |
| `districts` | One district | `district_id` | Public Berka data | Regional attributes reflect the source period |

## Analytical marts

| Table | Grain | Purpose |
|---|---|---|
| `mart_account_month` | Account-month with a posting | Monthly account activity and ending balance |
| `mart_monthly_performance` | Calendar month | Portfolio activity, value, and cash-flow KPIs |
| `mart_account_activation` | Account | First meaningful activity and 30/60/90-day activation |
| `mart_cohort_engagement` | Opening cohort and exact month number | Behavioural cohort engagement |
| `mart_account_360` | Account | Owner, activity, balance, card, and loan features |
| `mart_loan_portfolio` | Loan | Loan status and observed risk flags |
| `mart_customer_segments` | Account | Auditable segment assignment and action |
| `mart_segment_summary` | Segment | Portfolio share, behaviour, balance, and risk summary |

All marts are rebuilt from SQL files in `sql/marts/`; the generated DuckDB database remains local and is ignored by Git.
