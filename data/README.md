# Data

## Selected backbone dataset

**Berka / PKDD'99 Financial Dataset** — anonymised relational banking data released for the PKDD'99 Discovery Challenge.

- Retrieval date: 2026-10-04.
- Primary catalogue: https://relational.fel.cvut.cz/dataset/Financial
- Original challenge archive: `data_berka.zip` from the Prague University of Economics and Business challenge site; the original host was unavailable during setup.
- Retrieval fallback used locally: https://github.com/jlacko/berka-dataset
- Contents: accounts, clients, dispositions, cards, districts, loans, standing orders, and transactions.
- Scale: 1,079,680 source records, including 1,056,320 transactions.
- Nature: historical anonymised Czech banking data, not NovaPay data.
- Limitation: activity is from the 1990s and should not be treated as representative of current digital-wallet behaviour.

The raw files and generated database are intentionally ignored by Git. Do not claim that these records came from a modern fintech or a named real company.

## Rebuild

```bash
source .venv/bin/activate
python src/ingestion/build_berka_database.py
```

This creates `data/processed/novapay.duckdb` plus a table-level quality profile.

- `raw/`: immutable source files.
- `interim/`: validated and cleaned intermediate tables.
- `processed/`: analytical marts, feature tables, and local DuckDB database.
