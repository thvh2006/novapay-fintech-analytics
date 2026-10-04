"""Verify that the local analytics environment is ready."""

import duckdb
import numpy as np
import pandas as pd
import sklearn


def main() -> None:
    frame = pd.DataFrame({"amount": [10.0, 20.0, 30.0]})
    result = duckdb.from_df(frame).aggregate("sum(amount) as total").fetchone()[0]
    assert np.isclose(result, 60.0)
    print("NovaPay environment OK")
    print(f"pandas={pd.__version__}; scikit-learn={sklearn.__version__}; duckdb={duckdb.__version__}")


def test_environment() -> None:
    """Exercise the core dataframe-to-SQL workflow."""
    frame = pd.DataFrame({"amount": [10.0, 20.0, 30.0]})
    result = duckdb.from_df(frame).aggregate("sum(amount) as total").fetchone()[0]
    assert np.isclose(result, 60.0)


if __name__ == "__main__":
    main()
