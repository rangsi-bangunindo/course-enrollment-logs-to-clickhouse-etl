# Course Enrollment Event Logs Data Mart ETL

A manual ETL project that processes course enrollment event logs into a star-schema data mart using ClickHouse. This project extracts semi-structured log data, transforms it into normalized tables, and loads it into a columnar database for analysis.

---

## 1. Project Structure

```text
course-enrollment-event-logs-mart-etl/
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
├── .env                             # Environment variables for ClickHouse credentials (excluded from version control)
├── .gitignore                       # Excludes .env, __pycache__, and compiled files
└── README.md                        # Project documentation
```

---

## 2. File Details

### `etl/main_etl.py`

- Entry point for executing the ETL pipeline manually.
- Coordinates log transformation and data loading sequentially.
- Logs step progress to the console.

### `etl/log_transformer.py`

- Parses raw enrollment logs and outputs normalized CSVs.
- Splits raw data into:
  - `dim_user.csv`
  - `dim_course.csv`
  - `dim_time.csv`
  - `fact_enrollment.csv`
- Ensures consistent formatting (e.g., UTF-8, header included).

### `etl/clickhouse_loader.py`

- Loads the processed CSVs into corresponding ClickHouse tables.
- Reads credentials from `.env`.
- Uses `clickhouse-connect` to insert rows using type-safe mapping.

### `sql/schema_definition.sql`

- DDL script for defining the ClickHouse schema.
- Implements `LowCardinality`, `Nullable`, and optimized partitioning.
- Intended to be executed once before loading any data.

### `data/raw/enrollment_logs.txt`

- Raw source logs with a semi-structured format.
- Each line represents one enrollment event.

### `data/processed/*.csv`

- Output of the transformation step.
- Structured files ready for direct ingestion into ClickHouse.

---

## 3. ETL Overview

1. **Transform**  
   Parses raw semi-structured event logs and converts them into structured CSV tables conforming to a star schema.

2. **Load**  
   Loads the resulting CSVs into a ClickHouse database using optimized table definitions for analytical workloads.

Each step is executed sequentially and manually through scripts. Automation is intentionally omitted to focus on clarity and transparency of each stage.

### Transform Step

Raw event logs are processed into four normalized tables:

- `dim_user.csv`
- `dim_course.csv`
- `dim_time.csv`
- `fact_enrollment.csv`

Transformation is handled by the `log_transformer.py` script. It parses each log entry, extracts structured fields, and groups them into dimension and fact records based on the star schema design.

To run the transformation:

```bash
python etl/main_etl.py
```

Output files will be saved in:

```bash
data/processed/
```

The transformation script ensures:

- No duplicates in dimension tables
- Consistent formatting for timestamps and identifiers
- Encoding is preserved as UTF-8 with headers

### Load Step

Transformed CSV files are loaded into ClickHouse dimension and fact tables using the `clickhouse_loader.py` script.

This script connects to the database using credentials stored in the `.env` file and performs data insertion using the official `clickhouse-connect` client.

To run the full ETL (transform + load):

```bash
python etl/main_etl.py
```

The loader handles:

- Column type conversion (e.g., string to `DateTime`, `UInt64`)
- Null value handling for `Nullable()` columns
- Row validation before insertion

All CSVs must be:

- Comma-separated
- UTF-8 encoded
- Contain header rows

The database schema is defined in:

```bash
sql/schema_definition.sql
```

---

## 4. Schema Overview

### Fact Table

- **fact_enrollment**  
  Captures enrollment transactions with foreign keys to dimension tables and relevant measures.

### Dimension Tables

- **dim_user**  
  Contains user information such as user ID, name, and city.

- **dim_course**  
  Contains course-related information such as course ID, name, and category.

- **dim_time**  
  Captures temporal breakdown of enrollment time, including date, year, month, day, and hour.

Each table is optimized using appropriate data types and indexing strategies for efficient querying in ClickHouse.

---

## 5. Data Types & Optimization

- **LowCardinality(String)**  
  Applied to columns with repeated string values such as `course_id`, `user_city`, and `promo_code`, reducing storage and improving performance.

- **Nullable(...)**  
  Used for optional fields like `promo_code` and `final_price`, allowing explicit `NULL` handling.

- **DateTime / Date**  
  Used to store time-based values with correct granularity, ensuring compatibility with time functions and partitioning.

- **UInt32 / UInt64**  
  Chosen for numeric identifiers and measures to provide sufficient range with optimized memory usage.

- **PARTITION BY**  
  Time-based partitioning (e.g., `toYYYYMM(time_id)`) improves data management and range queries.

- **ORDER BY**  
  Defined using a combination of dimension keys and time to enable fast filtered queries on frequently queried columns.

---

## 6. Environment Setup

### Python Environment

- Recommended version: `Python 3.10+`.
- Dependencies are managed using a virtual environment.

### Virtual Environment Setup

```bash
python -m venv .venv
.venv\Scripts\activate         # On Windows (PowerShell)
source .venv/bin/activate      # On macOS/Linux
```

### Install Required Packages

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the root directory:

```env
CLICKHOUSE_HOST=clickhouse_host
CLICKHOUSE_PORT=8123
CLICKHOUSE_DB=database_name
CLICKHOUSE_USER=username
CLICKHOUSE_PASSWORD=password
```

---

## 7. How to Run

### Step 1: Place Raw Data

Place the raw enrollment log file in the following directory:

```bash
data/raw/event_logs.txt
```

### Step 2: Run the ETL Pipeline

Execute the ETL orchestration script:

```bash
python etl/main_etl.py
```

This script performs the following steps:

1. Parses raw logs into structured tables.
2. Writes CSV outputs to `data/processed/`.
3. Loads those CSVs into ClickHouse via the `clickhouse_loader.py` module.

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

- **Unexpected EOF while reading bytes**  
  Cause: Corrupted or incomplete CSV files.  
  Fix: Regenerate processed files by re-running the transformation step.

- **'str' object has no attribute 'timestamp'**  
  Cause: Datetime fields are still strings instead of Python datetime objects.  
  Fix: Ensure `pd.to_datetime()` is applied to datetime columns before loading.

- **Cannot parse input: expected ','**  
  Cause: Attempting to run `INSERT ... INFILE` syntax incorrectly in DBeaver or ClickHouse CLI.  
  Fix: Use `clickhouse_loader.py` for loading CSV files programmatically.

- **Permission errors when activating virtual environment**  
  Cause: Windows PowerShell script execution is disabled by default.  
  Fix: Run the following command with admin rights to allow scripts:

  ```powershell
  Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

- **Duplicate rows in ClickHouse**  
  Cause: ETL script run multiple times without clearing tables.  
  Fix: Run the cleanup query:

  ```sql
  TRUNCATE TABLE <table_name>;
  ```

Refer to transformation and loading logs for more detailed error context.
