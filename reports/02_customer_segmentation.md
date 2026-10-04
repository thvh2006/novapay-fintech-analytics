# Customer Segmentation

## Objective

Turn account-level behaviour into a small set of mutually exclusive groups that product, growth, service, and risk teams can act on. The segmentation is deliberately rule-based: every assignment can be explained from observed data without claiming predictive or causal accuracy.

## Feature design

The model combines:

- meaningful transaction count and active months, excluding `unspecified` system postings and opening cash deposits;
- lifetime credit value and latest recorded balance;
- card ownership and latest loan status;
- days to first meaningful activity;
- engagement recency as of 1998-12-31.

Thresholds use portfolio medians and upper quartiles. Rules are evaluated in priority order so each of the 4,500 accounts receives exactly one segment.

## Segment results

| Segment | Accounts | Share | Avg. activation days | Avg. engaged transactions | Avg. latest balance (CZK) |
|---|---:|---:|---:|---:|---:|
| Light relationship | 1,964 | 43.6% | 53.2 | 81.5 | 39,590 |
| Core transactional | 1,357 | 30.2% | 40.3 | 225.6 | 37,827 |
| Healthy borrower | 525 | 11.7% | 45.8 | 174.6 | 47,966 |
| Card-led engaged | 275 | 6.1% | 49.2 | 211.0 | 64,182 |
| High-value relationship | 274 | 6.1% | 42.3 | 301.9 | 83,269 |
| Risk watch | 105 | 2.3% | 57.7 | 169.2 | 22,929 |

## Rule hierarchy and actions

1. **Risk watch:** negative latest balance or loan status `B`/`D`. Review balances, repayment support, and alerts before cross-selling.
2. **High-value relationship:** top-quartile lifetime credits, latest balance, and engaged transactions. Protect service quality and test premium benefits.
3. **Healthy borrower:** completed-good or active-good loan. Provide relevant servicing and repayment reminders.
4. **Card-led engaged:** cardholder with above-median meaningful transactions. Deepen card usage through merchant or recurring-payment offers.
5. **Core transactional:** above-median engagement with no higher-priority flag. Promote card adoption and additional account features.
6. **Light relationship:** below-median engagement with no higher-priority flag. Use onboarding education and low-friction activation nudges.

## Validation

- 4,500 segment rows for 4,500 distinct accounts.
- Zero null assignments and six expected segments.
- Segment shares reconcile to 100.0%.
- All 39 negative-balance accounts and all 76 problem-loan accounts are captured by `Risk watch`.
- The risk flags overlap: 105 unique accounts contain 115 total flags.
- Automated tests protect account uniqueness, segment completeness, risk capture, and portfolio reconciliation.

## Interpretation

The largest opportunity is activation and relationship depth, not broad risk treatment. `Light relationship` accounts represent 43.6% of the portfolio and take the longest on average to activate. `Core transactional` adds another 30.2% with above-median behaviour but no higher-priority card or loan relationship.

The high-value group is only 6.1% of accounts but has the strongest engagement and average ending balance. It should receive service-protection experiments rather than undifferentiated acquisition messaging.

## Limitations

- Thresholds are descriptive and specific to this historical portfolio.
- Lifetime values are affected by different account tenures.
- Actions are hypotheses to test, not estimated causal impacts.
- Sensitive characteristics such as age and gender are not used in assignment rules.
