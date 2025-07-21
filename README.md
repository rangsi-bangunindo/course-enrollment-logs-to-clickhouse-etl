# Course Enrollment ETL: Event Logs to ClickHouse

An ETL project that processes course enrollment event logs into a star-schema data mart using ClickHouse, with each step executed sequentially via modular scripts. This project extracts semi-structured log data, transforms it into normalized tables, and loads it into a columnar database for analysis.

---

## 1. Project Structure

```text
course-enrollment-logs-to-clickhouse-etl/
├── data/
│   ├── raw/                         # Input text log files
│   │   └── enrollment_events.txt    # Raw enrollment event logs
│   └── processed/                   # Output CSV files
│       ├── dim_user.csv
│       ├── dim_course.csv
│       ├── dim_time.csv
│       └── fact_enrollment.csv
├── etl/
│   ├── main_etl.py                  # Orchestrates the ETL process
│   ├── log_transformer.py           # Parses and transforms raw logs into CSVs
│   └── clickhouse_loader.py         # Loads CSVs into ClickHouse tables
├── sql/
│   └── schema_definition.sql        # DDL script to create dimension and fact tables
├── docs/
│   └── star-schema-etl-report.pdf   # Documentation of the ETL and star schema design
├── requirements.txt                 # Python dependencies
├── .env                             # Environment variables for ClickHouse credentials
├── .gitignore                       # Excludes .env, __pycache__, and compiled files
└── README.md                        # Project overview and usage guide
```

---

## 2. File Overview

- **`etl/main_etl.py`**  
  Pipeline entry point. Executes the transformation and loading steps in sequence with console logging.

- **`etl/log_transformer.py`**  
  Parses raw event logs into four normalized CSV files:
  `dim_user.csv`, `dim_course.csv`, `dim_time.csv`, and `fact_enrollment.csv`.  
  Outputs are UTF-8 encoded with headers.

- **`etl/clickhouse_loader.py`**  
  Loads the transformed CSVs into ClickHouse using `clickhouse-connect`.  
  Reads database credentials from `.env` and handles type-safe insertions.

- **`sql/schema_definition.sql`**  
  DDL script for creating ClickHouse tables with `LowCardinality`, `Nullable`, and partitioning optimizations.  
  Intended for one-time setup.

- **`data/raw/enrollment_logs.txt`**  
  Raw semi-structured source file. Each line contains a single enrollment event.

- **`data/processed/*.csv`**  
  Output directory for structured CSVs generated during the transformation step.

---

## 3. ETL Overview

This ETL pipeline processes raw event logs into normalized CSVs and loads them into ClickHouse using modular Python scripts.

### Transform

Parses semi-structured logs into four tables:

- `dim_user.csv`
- `dim_course.csv`
- `dim_time.csv`
- `fact_enrollment.csv`

Handled by `etl/log_transformer.py`. Ensures:

- No duplicates in dimensions
- Standardized timestamps and formats
- UTF-8 encoding with headers

Run:

```bash
python etl/main_etl.py
```

Output: `data/processed/`

### Load

Inserts structured CSVs into ClickHouse using `etl/clickhouse_loader.py`.

Features:

- Type conversion (e.g., string → `DateTime`, `UInt64`)
- Null handling and row validation

Run:

```bash
python etl/main_etl.py
```

Schema: `sql/schema_definition.sql`  
Credentials: `.env`

CSV requirements:

- Comma-separated
- UTF-8 encoded
- With header rows

---

## 4. Schema Overview

This star schema supports efficient analytical queries on course enrollment data in ClickHouse.

1. **Fact Table: `fact_enrollment`**

   | Column        | Data Type                          | Description                                                       |
   | ------------- | ---------------------------------- | ----------------------------------------------------------------- |
   | `time_id`     | `DateTime`                         | Timestamp of the enrollment event                                 |
   | `user_id`     | `UInt64`                           | References `dim_user.user_id`                                     |
   | `course_id`   | `LowCardinality(String)`           | References `dim_course.course_id`                                 |
   | `price`       | `UInt32`                           | Original price of the course                                      |
   | `promo_code`  | `LowCardinality(Nullable(String))` | Promo code used if available, but discount value is not recorded. |
   | `final_price` | `Nullable(UInt32)`                 | Price after discount (if any)                                     |

2. **Dimension Table: `dim_user`**

   | Column      | Data Type                | Description       |
   | ----------- | ------------------------ | ----------------- |
   | `user_id`   | `UInt64`                 | Unique identifier |
   | `user_name` | `String`                 | Full name         |
   | `user_city` | `LowCardinality(String)` | City of residence |

3. **Dimension Table: `dim_course`**

   | Column        | Data Type                | Description              |
   | ------------- | ------------------------ | ------------------------ |
   | `course_id`   | `LowCardinality(String)` | Unique course identifier |
   | `course_name` | `String`                 | Title of the course      |
   | `category`    | `LowCardinality(String)` | Category of the course   |

4. **Dimension Table: `dim_time`**

   | Column    | Data Type  | Description                |
   | --------- | ---------- | -------------------------- |
   | `time_id` | `DateTime` | Timestamp surrogate key    |
   | `date`    | `Date`     | Calendar date (YYYY-MM-DD) |
   | `year`    | `UInt16`   | Year component             |
   | `month`   | `UInt8`    | Month component            |
   | `day`     | `UInt8`    | Day component              |
   | `hour`    | `UInt8`    | Hour of the day (0–23)     |

---

## 5. Data Types & Optimization Strategies in ClickHouse

ClickHouse offers fine-grained control over storage and performance through type-level and schema-level optimizations. Below is a breakdown of the key choices made in this project, along with comparisons to defaults in other columnar databases:

| Feature             | Implementation in ClickHouse             | Why It Matters                                  | In Other Systems                                                    |
| ------------------- | ---------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------- |
| **String Handling** | `LowCardinality(String)`                 | Reduces memory usage and speeds up filters      | Often handled automatically (e.g., dictionary encoding in BigQuery) |
| **Optional Fields** | `Nullable(...)`                          | Enables explicit `NULL` support                 | Usually implicit, sometimes less efficient                          |
| **Timestamps**      | `DateTime`, `Date`                       | Precise granularity; supports time functions    | Often `TIMESTAMP` with fewer tuning options                         |
| **Numeric IDs**     | `UInt32`, `UInt64`                       | Space-efficient for positive integers           | Commonly `INT`/`BIGINT`, often signed                               |
| **Partitioning**    | `PARTITION BY toYYYYMM(time_id)`         | Improves range queries and time-based retention | Often abstracted, e.g., partition decorators                        |
| **Indexing**        | `ORDER BY (course_id, time_id, user_id)` | Enables fast scans and index-aware queries      | Redshift uses sort keys; BigQuery relies on column pruning          |

> **Takeaway**: Unlike BigQuery or Redshift which abstract many storage optimizations, ClickHouse requires **explicit design decisions**, but rewards that effort with **faster query performance** and **lower storage cost** when done correctly.

---

## 6. Environment Setup

### Python Environment

- Recommended version: `Python 3.10+`.
- Dependencies are managed using a virtual environment.

### Virtual Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate         # On Windows
source .venv/bin/activate      # On macOS/Linux
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
CLICKHOUSE_HOST=<your_clickhouse_host>
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB=<your_database_name>
CLICKHOUSE_USER=<your_clickhouse_username>
CLICKHOUSE_PASSWORD=<your_clickhouse_password>
```

---

## 7. How to Run

### Step 1: Place Raw Data

Place the raw enrollment log file in the following directory:

```bash
data/raw/enrollment_logs.txt
```

### Step 2: Run the ETL Pipeline

Execute the ETL orchestration script:

```bash
python etl/main_etl.py
```

This script performs the following steps:

1. Parses raw logs into structured tables.
2. Writes CSV outputs to `data/processed/`.
3. Loads those CSVs into ClickHouse via the `etl/clickhouse_loader.py` module.

### Step 3: Query the Data

Once loaded, the tables in ClickHouse are ready for analytical queries using SQL clients such as DBeaver.

---

## 8. Error Handling & Logging

- **Try/Except Blocks**  
  Used in both transformation and load stages to catch and report errors without stopping the entire pipeline.

- **Descriptive Console Messages**  
  Each step logs its progress with clear prefixes and status messages, such as:

  - `Loading dim_user from ...`
  - `Successfully loaded ...`
  - `Failed to load ...: <error message>`

- **Row-Level Warnings (if applicable)**  
  During loading, malformed or empty rows are skipped with a printed warning and raw content preview for easier diagnosis.

- **Exit on Critical Failures**  
  The transformation step uses `sys.exit(1)` to halt the ETL process if parsing fails early.

This approach ensures visibility of process status while enabling partial successes in a multi-stage ETL execution.

---

## 9. Troubleshooting Tips

- **EOF error during file read**  
  **Cause**: Incomplete or corrupted CSV output.  
  **Fix**: Delete `data/processed/` and re-run `etl/log_transformer.py`.

- **`'str' object has no attribute 'timestamp'`**  
  **Cause**: Datetime columns not converted properly.  
  **Fix**: Apply `pd.to_datetime()` before transformations or loads.

- **ClickHouse CSV parse error (e.g., "expected ','")**  
  **Cause**: Manual `INSERT ... INFILE` execution misused.  
  **Fix**: Always use `etl/clickhouse_loader.py` to load CSVs.

- **Duplicate rows in fact or dimension tables**  
  **Cause**: Re-running ETL without clearing existing records.  
  **Fix**: Run:

  ```sql
  TRUNCATE TABLE <table_name>;
  ```

> Check transformation and loading logs for full stack traces and error context.
