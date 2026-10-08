import numpy as np
import pandas as pd
import pytest

from src.models.loan_default import assign_temporal_partitions, classification_metrics
from src.validation.contracts import assert_point_in_time_features, assert_unique_non_null_key


def test_temporal_partitions_are_ordered_and_keep_dates_together() -> None:
    frame = pd.DataFrame(
        {
            "loan_id": range(1, 13),
            "loan_date": pd.date_range("2020-01-01", periods=6).repeat(2),
        }
    )
    result, _ = assign_temporal_partitions(frame)
    assert set(result["partition"]) == {"development", "calibration", "oot"}
    assert result.groupby("loan_date")["partition"].nunique().max() == 1
    assert result.loc[result["partition"].eq("development"), "loan_date"].max() < result.loc[
        result["partition"].eq("calibration"), "loan_date"
    ].min()
    assert result.loc[result["partition"].eq("calibration"), "loan_date"].max() < result.loc[
        result["partition"].eq("oot"), "loan_date"
    ].min()


def test_point_in_time_contract_rejects_same_day_feature() -> None:
    invalid = pd.DataFrame(
        {"loan_date": ["2020-01-02"], "feature_cutoff": ["2020-01-02"]}
    )
    with pytest.raises(ValueError, match="strictly earlier"):
        assert_point_in_time_features(invalid, "loan_date", "feature_cutoff")


def test_key_contract_rejects_duplicates() -> None:
    with pytest.raises(ValueError, match="duplicate"):
        assert_unique_non_null_key(pd.DataFrame({"loan_id": [1, 1]}), "loan_id")


def test_classification_metrics_have_expected_direction() -> None:
    metrics = classification_metrics(pd.Series([0, 0, 1, 1]), np.array([0.1, 0.2, 0.8, 0.9]))
    assert metrics["average_precision"] == pytest.approx(1.0)
    assert metrics["roc_auc"] == pytest.approx(1.0)
    assert metrics["brier_score"] < 0.05
    assert metrics["positive_labels"] == 2
