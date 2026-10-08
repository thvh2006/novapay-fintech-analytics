# Historical loan-risk baseline: temporal validation

## Purpose

This extension tests whether the repository can build a prediction-ready, point-in-time feature set without overstating what the historical source supports. The target is source status `B` or `D`. It is called an **observed problem-loan label**, not regulatory default, expected loss, or a modern credit-risk outcome.

## Leakage controls

- Every transaction feature uses rows with `transaction_date < loan_date`.
- No latest-account snapshot or post-origination transaction enters the model.
- Whole origination dates are assigned to one partition only.
- The regularised logistic model is fitted on development (through 22 May 1997).
- Platt calibration is fitted on the later calibration window (through 23 January 1998).
- The last 141 loans remain locked OOT until the pipeline is fixed.

Features cover loan terms known at origination, account tenure, prior transaction counts and flows, prior balance behaviour, statement frequency, and coarse district context. No protected characteristic is included.

## Results

| Window | Loans | Positive labels | Rate | AP | ROC-AUC | Brier |
|---|---:|---:|---:|---:|---:|---:|
| Development | 399 | 54 | 13.53% | 0.518 | 0.844 | 0.0928 |
| Calibration | 142 | 19 | 13.38% | 0.819 | 0.922 | 0.0525 |
| Locked OOT | 141 | **3** | **2.13%** | 0.618 | 0.966 | 0.0272 |

The late-window ranking metrics look strong, but the denominator is not strong enough for a production conclusion. Average precision and ROC-AUC are based on only three positive outcomes. The positive-label rate drops 84% relative to development.

## Decision and next evidence

**Decision: research baseline only. Do not use for automated approval, pricing, limit, or decline decisions.**

Before promotion, a lender would need:

1. a prospectively defined outcome window and explicit label-maturity timestamp;
2. more recent originations and enough mature bad outcomes for stable uncertainty estimates;
3. a non-linear challenger evaluated under the same locked design;
4. calibration by relevant product/time subgroups and reject-inference analysis;
5. fairness, explainability, adverse-action, privacy, and human-review governance;
6. business evaluation in expected-loss terms using probability of default, exposure at default, and loss given default—not transaction amount alone.

The correct insight is therefore not “AUC 0.97 means the model is ready.” It is that disciplined temporal construction can expose a validity problem that a random split would hide.
