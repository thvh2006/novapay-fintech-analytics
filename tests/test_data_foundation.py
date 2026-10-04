"""Data-quality checks for the locally built Berka database."""

from pathlib import Path

import duckdb
import pytest

DATABASE_PATH = Path(__file__).resolve().parents[1] / "data" / "processed" / "novapay.duckdb"

pytestmark = pytest.mark.skipif(not DATABASE_PATH.exists(), reason="Local database not built")


@pytest.fixture(scope="module")
def connection():
    with duckdb.connect(DATABASE_PATH, read_only=True) as database:
        yield database


def test_expected_source_counts(connection) -> None:
    expected = {
        "accounts": 4_500,
        "clients": 5_369,
        "transactions": 1_056_320,
        "loans": 682,
    }
    for table_name, row_count in expected.items():
        actual = connection.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]
        assert actual == row_count


def test_transaction_keys_and_account_relationship(connection) -> None:
    null_or_duplicate_keys = connection.execute(
        """
        SELECT
            count(*) FILTER (WHERE transaction_id IS NULL)
            + count(*) - count(DISTINCT transaction_id)
        FROM transactions
        """
    ).fetchone()[0]
    orphan_transactions = connection.execute(
        """
        SELECT count(*)
        FROM transactions t
        LEFT JOIN accounts a USING (account_id)
        WHERE a.account_id IS NULL
        """
    ).fetchone()[0]
    assert null_or_duplicate_keys == 0
    assert orphan_transactions == 0


def test_transaction_date_range(connection) -> None:
    first_date, last_date = connection.execute(
        "SELECT min(transaction_date), max(transaction_date) FROM transactions"
    ).fetchone()
    assert first_date.isoformat() == "1993-01-01"
    assert last_date.isoformat() == "1998-12-31"


def test_dashboard_marts_have_expected_grain(connection) -> None:
    account_month_rows = connection.execute("SELECT count(*) FROM mart_account_month").fetchone()[0]
    account_360_rows = connection.execute("SELECT count(*) FROM mart_account_360").fetchone()[0]
    monthly_rows = connection.execute("SELECT count(*) FROM mart_monthly_performance").fetchone()[0]
    assert account_month_rows > account_360_rows
    assert account_360_rows == 4_500
    assert monthly_rows == 72


def test_activation_definition_excludes_opening_deposit(connection) -> None:
    total_accounts, activated_30d, median_days = connection.execute(
        """
        SELECT
            count(*),
            count(*) FILTER (WHERE activated_within_30d),
            median(days_to_activation)
        FROM mart_account_activation
        """
    ).fetchone()
    assert total_accounts == 4_500
    assert activated_30d == 2_268
    assert median_days == 30


def test_customer_segments_are_complete_and_mutually_exclusive(connection) -> None:
    total_accounts, distinct_accounts, null_segments, segment_count = connection.execute(
        """
        SELECT
            count(*),
            count(DISTINCT account_id),
            count(*) FILTER (WHERE customer_segment IS NULL),
            count(DISTINCT customer_segment)
        FROM mart_customer_segments
        """
    ).fetchone()
    assert total_accounts == 4_500
    assert distinct_accounts == 4_500
    assert null_segments == 0
    assert segment_count == 6


def test_risk_watch_segment_captures_all_observed_risk_flags(connection) -> None:
    missed_risk_accounts = connection.execute(
        """
        SELECT count(*)
        FROM mart_customer_segments
        WHERE (latest_balance_czk < 0 OR latest_loan_status IN ('B', 'D'))
          AND customer_segment <> 'Risk watch'
        """
    ).fetchone()[0]
    assert missed_risk_accounts == 0


def test_segment_summary_reconciles_to_portfolio(connection) -> None:
    accounts, portfolio_share = connection.execute(
        """
        SELECT sum(accounts), sum(portfolio_share)
        FROM mart_segment_summary
        """
    ).fetchone()
    assert accounts == 4_500
    assert portfolio_share == pytest.approx(1.0, abs=0.001)
