# Executive Decision Memo

## Recommendation

Prioritise activation and relationship-depth interventions while keeping a small, separate risk-review path. The portfolio has broad engagement potential, but raw ledger postings overstate customer activity and should not drive product decisions.

## Evidence

- Only 50.4% of accounts reach meaningful activity within 30 days; the rate rises to 84.1% within 60 days.
- `Light relationship` represents 1,964 accounts, or 43.6% of the portfolio, and has the slowest average activation at 53.2 days.
- `Core transactional` represents 1,357 accounts with above-median engagement and a clear card-adoption opportunity.
- `High-value relationship` includes 274 accounts with an average latest balance of CZK 83,269 and the highest average engagement.
- `Risk watch` is concentrated in 105 accounts and captures all observed negative balances and problem-loan statuses.

## Actions

### 1. Improve the first 30 days

Instrument onboarding steps and test reminders before day 30. Measure movement in the current activation definition rather than counting the opening deposit.

### 2. Convert transactional relationships

Target the `Core transactional` segment with a measured card-adoption or recurring-payment offer. Use a holdout group and define success before launch.

### 3. Protect high-value service

Monitor service quality and attrition signals for `High-value relationship` accounts. Test premium support or relationship benefits without assuming balance equals profitability.

### 4. Separate risk treatment from growth campaigns

Route `Risk watch` accounts to review, balance alerts, and repayment support. Do not use the segment as an automated lending decision.

## Measurement plan

- Primary activation KPI: meaningful activity within 30 days.
- Relationship KPI: card adoption or additional feature use among eligible core accounts.
- Guardrails: negative balances, problem-loan transitions, and customer complaints.
- Experiment requirement: randomised holdout where feasible; otherwise use a documented pre/post comparison with matched eligibility.

## Important caveat

The source is historical anonymised banking data from 1993–1998. These findings demonstrate analytical method and decision framing; they are not estimates of current digital-fintech performance.
