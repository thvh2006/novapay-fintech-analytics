"""Train and evaluate a point-in-time historical loan-risk baseline."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import duckdb
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.models.loan_default import (
    assign_temporal_partitions,
    build_logistic_pipeline,
    calibrated_probability,
    classification_metrics,
    fit_platt_calibrator,
)
from src.validation.contracts import assert_point_in_time_features

DATABASE = ROOT / "data" / "processed" / "novapay.duckdb"
REPORTS = ROOT / "reports"

NUMERIC_FEATURES = [
    "loan_amount_czk",
    "duration_months",
    "monthly_payment_czk",
    "account_tenure_days",
    "prior_transaction_count",
    "prior_credit_czk",
    "prior_debit_czk",
    "prior_net_flow_czk",
    "prior_latest_balance_czk",
    "prior_min_balance_czk",
    "prior_active_days",
    "average_salary_czk",
    "unemployment_rate_1996",
]
CATEGORICAL_FEATURES = ["statement_frequency", "region_name"]


def loan_feature_query() -> str:
    """Return features known before origination; no post-loan account snapshot is used."""
    return """
        WITH prior_transactions AS (
            SELECT
                l.loan_id,
                count(t.transaction_id) AS prior_transaction_count,
                sum(t.amount_czk) FILTER (WHERE t.transaction_direction = 'credit')
                    AS prior_credit_czk,
                sum(t.amount_czk) FILTER (WHERE t.transaction_direction = 'debit')
                    AS prior_debit_czk,
                sum(CASE WHEN t.transaction_direction = 'credit' THEN t.amount_czk
                         ELSE -t.amount_czk END) AS prior_net_flow_czk,
                arg_max(
                    t.balance_czk,
                    epoch(t.transaction_date) * 10000000 + t.transaction_id
                ) AS prior_latest_balance_czk,
                min(t.balance_czk) AS prior_min_balance_czk,
                count(DISTINCT t.transaction_date) AS prior_active_days,
                max(t.transaction_date) AS feature_cutoff_date
            FROM loans l
            LEFT JOIN transactions t
              ON t.account_id = l.account_id
             AND t.transaction_date < l.loan_date
            GROUP BY l.loan_id
        )
        SELECT
            l.loan_id,
            l.loan_date,
            CASE WHEN l.loan_status IN ('B', 'D') THEN 1 ELSE 0 END AS observed_problem_loan,
            l.loan_amount_czk,
            l.duration_months,
            l.monthly_payment_czk,
            date_diff('day', a.opened_date, l.loan_date) AS account_tenure_days,
            a.statement_frequency,
            d.region_name,
            d.average_salary_czk,
            d.unemployment_rate_1996,
            p.prior_transaction_count,
            coalesce(p.prior_credit_czk, 0) AS prior_credit_czk,
            coalesce(p.prior_debit_czk, 0) AS prior_debit_czk,
            coalesce(p.prior_net_flow_czk, 0) AS prior_net_flow_czk,
            p.prior_latest_balance_czk,
            p.prior_min_balance_czk,
            p.prior_active_days,
            p.feature_cutoff_date
        FROM loans l
        JOIN accounts a USING (account_id)
        LEFT JOIN districts d USING (district_id)
        LEFT JOIN prior_transactions p USING (loan_id)
        ORDER BY l.loan_date, l.loan_id
    """


def main() -> None:
    if not DATABASE.exists():
        raise FileNotFoundError(f"Build the local database first: {DATABASE}")
    with duckdb.connect(DATABASE, read_only=True) as connection:
        frame = connection.execute(loan_feature_query()).fetch_df()

    assert_point_in_time_features(frame, "loan_date", "feature_cutoff_date")
    frame, boundaries = assign_temporal_partitions(frame)
    model = build_logistic_pipeline(NUMERIC_FEATURES, CATEGORICAL_FEATURES)
    development = frame.loc[frame["partition"].eq("development")]
    calibration = frame.loc[frame["partition"].eq("calibration")]
    model.fit(development[NUMERIC_FEATURES + CATEGORICAL_FEATURES], development["observed_problem_loan"])
    calibrator = fit_platt_calibrator(
        model,
        calibration[NUMERIC_FEATURES + CATEGORICAL_FEATURES],
        calibration["observed_problem_loan"],
    )

    metrics = []
    for partition in ["development", "calibration", "oot"]:
        sample = frame.loc[frame["partition"].eq(partition)]
        probability = calibrated_probability(
            model, calibrator, sample[NUMERIC_FEATURES + CATEGORICAL_FEATURES]
        )
        metrics.append(
            {"partition": partition, **classification_metrics(sample["observed_problem_loan"], probability)}
        )

    REPORTS.mkdir(exist_ok=True)
    pd.DataFrame(metrics).to_csv(REPORTS / "loan_risk_temporal_metrics.csv", index=False)
    payload = {
        "label": "source status B or D; historical observed outcome, not regulatory default",
        "development_end": boundaries.development_end.date().isoformat(),
        "calibration_end": boundaries.calibration_end.date().isoformat(),
        "features": NUMERIC_FEATURES + CATEGORICAL_FEATURES,
        "probability_calibration": "Platt scaling fitted only on the later calibration window",
        "metrics": metrics,
        "validity_warning": (
            "Locked OOT contains only three positive labels and a sharply lower outcome rate; "
            "ranking metrics are unstable and outcome maturity or regime change cannot be separated."
        ),
        "decision": "research baseline only; do not use for automated credit decisions",
    }
    (REPORTS / "loan_risk_temporal_validation.json").write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )
    print(json.dumps(payload, indent=2))


if __name__ == "__main__":
    main()
