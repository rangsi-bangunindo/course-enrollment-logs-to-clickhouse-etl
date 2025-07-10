# Course Enrollment Event Logs Data Mart ETL

A manual ETL project that processes course enrollment event logs into a star-schema data mart using ClickHouse. Built to simulate a production-grade ETL workflow, this project extracts semi-structured raw logs, transforms them into normalized dimension and fact tables, and loads them into ClickHouse for analysis.

---

## Project Structure

```
course-enrollment-event-logs-mart-etl/
├── data/
│   ├── raw/                      # Input: a text file
│   └── processed/                # Output: normalized CSV files
├── etl/
│   ├── main_etl.py               # ETL entrypoint (orchestrates transform + load)
│   ├── log_transformer.py        # Raw log parser into star schema CSVs
│   └── clickhouse_loader.py      # CSV loader into ClickHouse
├── sql/
│   └── schema_definition.sql     # CREATE TABLE scripts (dim + fact)
├── .env                          # ClickHouse credentials (excluded from Git)
├── .gitignore
└── README.md
```

---

## ETL Steps

### 1. Transform Raw Logs

Transform raw enrollment events into CSV tables for:

- dim_user
- dim_course
- dim_time
- fact_enrollment

Run this from project root:

```bash
python etl/main_etl.py
```

Output will be saved to `data/processed/`

Note: The load step is currently not included and will be handled by `clickhouse_loader.py`.

---

### 2. Create Tables in ClickHouse

Execute the following script in DBeaver or ClickHouse CLI:

```sql
-- sql/schema_definition.sql
```

---

## Notes

- CSV format is UTF-8, comma-delimited, and assumes headers are present.
- Column types are optimized using `LowCardinality`, `Nullable`, and appropriate `PARTITION BY` / `ORDER BY` strategies.
