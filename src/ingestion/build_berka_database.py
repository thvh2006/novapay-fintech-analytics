"""Build the local DuckDB analytical database from the Berka raw files."""

from __future__ import annotations

import csv
from pathlib import Path

import duckdb

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DIR / "novapay.duckdb"

SOURCE_FILES = {
    "account": "account.asc",
    "card": "card.asc",
    "client": "client.asc",
    "disp": "disp.asc",
    "district": "district.asc",
    "loan": "loan.asc",
    "orders": "order.asc",
    "trans": "trans.asc",
}


def require_source_files() -> None:
    missing = [filename for filename in SOURCE_FILES.values() if not (RAW_DIR / filename).exists()]
    if missing:
        joined = ", ".join(missing)
        raise FileNotFoundError(f"Missing source files in {RAW_DIR}: {joined}")


def load_raw_tables(connection: duckdb.DuckDBPyConnection) -> None:
    for table_name, filename in SOURCE_FILES.items():
        source_path = (RAW_DIR / filename).as_posix().replace("'", "''")
        connection.execute(
            f"""
            CREATE OR REPLACE TABLE raw_{table_name} AS
            SELECT *
            FROM read_csv(
                '{source_path}',
                delim = ';',
                header = true,
                auto_detect = true,
                sample_size = -1,
                nullstr = ''
            )
            """
        )


def create_clean_tables(connection: duckdb.DuckDBPyConnection) -> None:
    connection.execute(
        """
        CREATE OR REPLACE TABLE accounts AS
        SELECT
            account_id::BIGINT AS account_id,
            district_id::INTEGER AS district_id,
            CASE frequency
                WHEN 'POPLATEK MESICNE' THEN 'monthly'
                WHEN 'POPLATEK TYDNE' THEN 'weekly'
                WHEN 'POPLATEK PO OBRATU' THEN 'after_transaction'
                ELSE lower(frequency)
            END AS statement_frequency,
            make_date(
                1900 + (date::INTEGER // 10000),
                (date::INTEGER // 100) % 100,
                date::INTEGER % 100
            ) AS opened_date
        FROM raw_account;

        CREATE OR REPLACE TABLE clients AS
        WITH parsed AS (
            SELECT
                client_id::BIGINT AS client_id,
                birth_number::INTEGER AS birth_number,
                district_id::INTEGER AS district_id,
                (birth_number::INTEGER // 100) % 100 AS encoded_month
            FROM raw_client
        )
        SELECT
            client_id,
            district_id,
            CASE WHEN encoded_month > 50 THEN 'F' ELSE 'M' END AS gender,
            make_date(
                1900 + (birth_number // 10000),
                encoded_month - CASE WHEN encoded_month > 50 THEN 50 ELSE 0 END,
                birth_number % 100
            ) AS birth_date
        FROM parsed;

        CREATE OR REPLACE TABLE dispositions AS
        SELECT
            disp_id::BIGINT AS disposition_id,
            client_id::BIGINT AS client_id,
            account_id::BIGINT AS account_id,
            CASE type
                WHEN 'OWNER' THEN 'owner'
                WHEN 'DISPONENT' THEN 'authorized_user'
                ELSE lower(type)
            END AS disposition_type
        FROM raw_disp;

        CREATE OR REPLACE TABLE cards AS
        SELECT
            card_id::BIGINT AS card_id,
            disp_id::BIGINT AS disposition_id,
            lower(type) AS card_type,
            strptime('19' || issued::VARCHAR, '%Y%m%d %H:%M:%S')::DATE AS issued_date
        FROM raw_card;

        CREATE OR REPLACE TABLE districts AS
        SELECT
            A1::INTEGER AS district_id,
            A2::VARCHAR AS district_name,
            A3::VARCHAR AS region_name,
            A4::INTEGER AS population,
            A5::INTEGER AS municipalities_under_500,
            A6::INTEGER AS municipalities_500_1999,
            A7::INTEGER AS municipalities_2000_9999,
            A8::INTEGER AS municipalities_10000_plus,
            A9::INTEGER AS city_count,
            A10::DOUBLE AS urban_population_pct,
            A11::DOUBLE AS average_salary_czk,
            try_cast(A12 AS DOUBLE) AS unemployment_rate_1995,
            try_cast(A13 AS DOUBLE) AS unemployment_rate_1996,
            A14::DOUBLE AS entrepreneurs_per_1000,
            try_cast(A15 AS INTEGER) AS crimes_1995,
            try_cast(A16 AS INTEGER) AS crimes_1996
        FROM raw_district;

        CREATE OR REPLACE TABLE loans AS
        SELECT
            loan_id::BIGINT AS loan_id,
            account_id::BIGINT AS account_id,
            make_date(
                1900 + (date::INTEGER // 10000),
                (date::INTEGER // 100) % 100,
                date::INTEGER % 100
            ) AS loan_date,
            amount::DOUBLE AS loan_amount_czk,
            duration::INTEGER AS duration_months,
            payments::DOUBLE AS monthly_payment_czk,
            status::VARCHAR AS loan_status
        FROM raw_loan;

        CREATE OR REPLACE TABLE standing_orders AS
        SELECT
            order_id::BIGINT AS order_id,
            account_id::BIGINT AS account_id,
            bank_to::VARCHAR AS destination_bank,
            account_to::BIGINT AS destination_account,
            amount::DOUBLE AS amount_czk,
            CASE k_symbol
                WHEN 'POJISTNE' THEN 'insurance'
                WHEN 'SIPO' THEN 'household'
                WHEN 'LEASING' THEN 'leasing'
                WHEN 'UVER' THEN 'loan_payment'
                ELSE coalesce(lower(k_symbol), 'unspecified')
            END AS payment_category
        FROM raw_orders;

        CREATE OR REPLACE TABLE transactions AS
        SELECT
            trans_id::BIGINT AS transaction_id,
            account_id::BIGINT AS account_id,
            make_date(
                1900 + (date::INTEGER // 10000),
                (date::INTEGER // 100) % 100,
                date::INTEGER % 100
            ) AS transaction_date,
            CASE type
                WHEN 'PRIJEM' THEN 'credit'
                WHEN 'VYDAJ' THEN 'debit'
                WHEN 'VYBER' THEN 'debit'
                ELSE lower(type)
            END AS transaction_direction,
            CASE operation
                WHEN 'VYBER KARTOU' THEN 'card_withdrawal'
                WHEN 'VKLAD' THEN 'cash_deposit'
                WHEN 'PREVOD Z UCTU' THEN 'bank_transfer_in'
                WHEN 'VYBER' THEN 'cash_withdrawal'
                WHEN 'PREVOD NA UCET' THEN 'bank_transfer_out'
                ELSE coalesce(lower(operation), 'unspecified')
            END AS operation_type,
            amount::DOUBLE AS amount_czk,
            balance::DOUBLE AS balance_czk,
            CASE k_symbol
                WHEN 'POJISTNE' THEN 'insurance'
                WHEN 'SLUZBY' THEN 'statement_fee'
                WHEN 'UROK' THEN 'interest_credit'
                WHEN 'SANKC. UROK' THEN 'penalty_interest'
                WHEN 'SIPO' THEN 'household'
                WHEN 'DUCHOD' THEN 'pension'
                WHEN 'UVER' THEN 'loan_payment'
                ELSE coalesce(lower(k_symbol), 'unspecified')
            END AS transaction_category,
            bank::VARCHAR AS counterparty_bank,
            account::BIGINT AS counterparty_account
        FROM raw_trans;
        """
    )


def validate_and_profile(connection: duckdb.DuckDBPyConnection) -> None:
    primary_keys = {
        "accounts": "account_id",
        "cards": "card_id",
        "clients": "client_id",
        "dispositions": "disposition_id",
        "districts": "district_id",
        "loans": "loan_id",
        "standing_orders": "order_id",
        "transactions": "transaction_id",
    }

    profile_rows: list[tuple[str, int, int, int]] = []
    for table_name, key_name in primary_keys.items():
        row_count, null_keys, duplicate_keys = connection.execute(
            f"""
            SELECT
                count(*) AS row_count,
                count(*) FILTER (WHERE {key_name} IS NULL) AS null_keys,
                count(*) - count(DISTINCT {key_name}) AS duplicate_keys
            FROM {table_name}
            """
        ).fetchone()
        profile_rows.append((table_name, row_count, null_keys, duplicate_keys))
        if null_keys or duplicate_keys:
            raise ValueError(
                f"Invalid primary key in {table_name}: null={null_keys}, duplicate={duplicate_keys}"
            )

    orphan_transactions = connection.execute(
        """
        SELECT count(*)
        FROM transactions t
        LEFT JOIN accounts a USING (account_id)
        WHERE a.account_id IS NULL
        """
    ).fetchone()[0]
    if orphan_transactions:
        raise ValueError(f"Found {orphan_transactions} transactions without an account")

    profile_path = PROCESSED_DIR / "table_profile.csv"
    with profile_path.open("w", newline="", encoding="utf-8") as output_file:
        writer = csv.writer(output_file)
        writer.writerow(["table_name", "row_count", "null_primary_keys", "duplicate_primary_keys"])
        writer.writerows(profile_rows)


def main() -> None:
    require_source_files()
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with duckdb.connect(DATABASE_PATH) as connection:
        load_raw_tables(connection)
        create_clean_tables(connection)
        validate_and_profile(connection)
    print(f"Built {DATABASE_PATH}")


if __name__ == "__main__":
    main()

