"""
Main entry point to run the manual ETL process for
the course-enrollment-event-logs-mart-etl project.

This script orchestrates the parsing, transformation,
and saving of raw event logs into normalized star schema tables.
"""

import sys
from pathlib import Path

# Run transformation
print("🔄 [1/1] Transforming logs into dimension and fact tables...")
try:
    import log_transformer
    print("✅ Transformation completed. CSV files saved in /data/processed/")
except Exception as e:
    print("❌ Transformation failed:", e)
    sys.exit(1)

# Future extension:
# from clickhouse_loader import load_to_clickhouse
# load_to_clickhouse(...)