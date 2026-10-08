"""Leakage-aware temporal baseline for the historical loan outcome label."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


@dataclass(frozen=True)
class TemporalBoundaries:
    development_end: pd.Timestamp
    calibration_end: pd.Timestamp


def assign_temporal_partitions(
    frame: pd.DataFrame,
    date_column: str = "loan_date",
    development_share: float = 0.60,
    calibration_share: float = 0.20,
) -> tuple[pd.DataFrame, TemporalBoundaries]:
    """Assign whole calendar dates to development, calibration, and locked OOT."""
    if not 0 < development_share < 1 or not 0 < calibration_share < 1:
        raise ValueError("partition shares must be between zero and one")
    if development_share + calibration_share >= 1:
        raise ValueError("development and calibration must leave a locked OOT partition")

    result = frame.copy()
    result[date_column] = pd.to_datetime(result[date_column])
    if result[date_column].isna().any():
        raise ValueError("observation dates cannot be missing")

    dates = np.array(sorted(result[date_column].dt.normalize().unique()))
    if len(dates) < 5:
        raise ValueError("at least five unique dates are required")
    development_index = min(int(len(dates) * development_share) - 1, len(dates) - 3)
    calibration_index = min(
        int(len(dates) * (development_share + calibration_share)) - 1,
        len(dates) - 2,
    )
    development_end = pd.Timestamp(dates[max(development_index, 0)])
    calibration_end = pd.Timestamp(dates[max(calibration_index, development_index + 1)])

    result["partition"] = np.select(
        [
            result[date_column] <= development_end,
            result[date_column] <= calibration_end,
        ],
        ["development", "calibration"],
        default="oot",
    )
    boundaries = TemporalBoundaries(development_end, calibration_end)
    return result.sort_values([date_column, "loan_id"], kind="stable"), boundaries


def build_logistic_pipeline(
    numeric_features: list[str], categorical_features: list[str]
) -> Pipeline:
    """Build an interpretable, regularised baseline with train-only preprocessing."""
    numeric = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="median")),
            ("scale", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        [
            ("imputer", SimpleImputer(strategy="most_frequent")),
            ("one_hot", OneHotEncoder(handle_unknown="ignore")),
        ]
    )
    transformer = ColumnTransformer(
        [("numeric", numeric, numeric_features), ("categorical", categorical, categorical_features)]
    )
    return Pipeline(
        [
            ("features", transformer),
            (
                "model",
                LogisticRegression(
                    class_weight="balanced",
                    max_iter=2_000,
                    C=0.25,
                    random_state=42,
                ),
            ),
        ]
    )


def classification_metrics(y_true: pd.Series, probability: np.ndarray) -> dict[str, float]:
    """Return discrimination and calibration metrics without threshold optimisation."""
    if pd.Series(y_true).nunique() < 2:
        raise ValueError("metrics require both outcome classes")
    return {
        "rows": len(y_true),
        "positive_labels": int(np.sum(y_true)),
        "problem_rate": float(np.mean(y_true)),
        "average_precision": float(average_precision_score(y_true, probability)),
        "roc_auc": float(roc_auc_score(y_true, probability)),
        "brier_score": float(brier_score_loss(y_true, probability)),
    }


def fit_platt_calibrator(
    fitted_model: Pipeline, features: pd.DataFrame, target: pd.Series
) -> LogisticRegression:
    """Fit a one-dimensional probability calibration model on a later time window."""
    calibrator = LogisticRegression(C=1_000_000, random_state=42)
    score = fitted_model.decision_function(features).reshape(-1, 1)
    calibrator.fit(score, target)
    return calibrator


def calibrated_probability(
    fitted_model: Pipeline, calibrator: LogisticRegression, features: pd.DataFrame
) -> np.ndarray:
    """Apply the later-window Platt calibrator to raw model scores."""
    score = fitted_model.decision_function(features).reshape(-1, 1)
    return calibrator.predict_proba(score)[:, 1]
