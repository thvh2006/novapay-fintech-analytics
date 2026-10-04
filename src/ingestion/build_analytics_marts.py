"""Execute the ordered SQL files that build dashboard-ready analytical marts."""

from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "novapay.duckdb"
MARTS_DIR = PROJECT_ROOT / "sql" / "marts"


def main() -> None:
    if not DATABASE_PATH.exists():
        raise FileNotFoundError(
            "Database not found. Run src/ingestion/build_berka_database.py first."
        )

    sql_files = sorted(MARTS_DIR.glob("*.sql"))
    if not sql_files:
        raise FileNotFoundError(f"No mart SQL files found in {MARTS_DIR}")

    with duckdb.connect(DATABASE_PATH) as connection:
        for sql_file in sql_files:
            connection.execute(sql_file.read_text(encoding="utf-8"))
            print(f"Executed {sql_file.name}")


if __name__ == "__main__":
    main()

