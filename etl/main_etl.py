"""
Main entry point to run the manual ETL process.
This script orchestrates the parsing, transformation,
and loading of raw event logs into normalized star schema tables.
"""

import sys

# Transform raw logs into dimension + fact tables
print("[1/2] Transforming logs into dimension and fact tables...")
try:
    import log_transformer
    print("Transformation completed. CSV files saved in /data/processed/")
except Exception as e:
    print("Transformation failed:", e)
    sys.exit(1)

# Load processed data into ClickHouse
print("[2/2] Loading CSVs into ClickHouse...")
try:
    import clickhouse_loader
    print("Loading completed.")
except Exception as e:
    print("Loading failed:", e)
    sys.exit(1)