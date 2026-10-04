"""Export dashboard-ready mart tables from DuckDB to CSV."""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "novapay.duckdb"
EXPORT_DIR = PROJECT_ROOT / "dashboard" / "data"

EXPORTS = {
    "monthly_performance.csv": "mart_monthly_performance",
    "account_activation.csv": "mart_account_activation",
    "cohort_engagement.csv": "mart_cohort_engagement",
    "account_360.csv": "mart_account_360",
    "loan_portfolio.csv": "mart_loan_portfolio",
    "customer_segments.csv": "mart_customer_segments",
    "segment_summary.csv": "mart_segment_summary",
}


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError("Build the local database and marts before exporting dashboard data.")

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(DATABASE_PATH, read_only=True) as connection:
        for filename, table_name in EXPORTS.items():
            destination = (EXPORT_DIR / filename).as_posix().replace("'", "''")
            connection.execute(
                f"COPY {table_name} TO '{destination}' (HEADER, DELIMITER ',')"
            )
            row_count = connection.execute(f"SELECT count(*) FROM {table_name}").fetchone()[0]
            print(f"Exported {filename}: {row_count:,} rows")


if __name__ == "__main__":
    main()
