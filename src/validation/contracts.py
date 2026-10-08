"""Small validation contracts that can run without the private local database."""

from __future__ import annotations

import pandas as pd


def assert_unique_non_null_key(frame: pd.DataFrame, key: str) -> None:
    """Fail loudly when a table violates its declared row grain."""
    if frame[key].isna().any():
        raise ValueError(f"{key} contains null values")
    if frame[key].duplicated().any():
        raise ValueError(f"{key} contains duplicate values")


def assert_point_in_time_features(
    frame: pd.DataFrame, observation_date: str, feature_cutoff_date: str
) -> None:
    """Ensure feature history ends strictly before the prediction observation."""
    observation = pd.to_datetime(frame[observation_date])
    cutoff = pd.to_datetime(frame[feature_cutoff_date])
    invalid = cutoff.notna() & (cutoff >= observation)
    if invalid.any():
        raise ValueError("feature cutoff must be strictly earlier than observation date")

