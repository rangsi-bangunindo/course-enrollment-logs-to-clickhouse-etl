"""
This script connects to ClickHouse and loads processed CSV files
into the corresponding dimension and fact tables.
"""

import os
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import clickhouse_connect

# Load environment variables
load_dotenv()

CLICKHOUSE_HOST = os.getenv("CLICKHOUSE_HOST")
CLICKHOUSE_PORT = int(os.getenv("CLICKHOUSE_PORT"))
CLICKHOUSE_DB = os.getenv("CLICKHOUSE_DB")
CLICKHOUSE_USER = os.getenv("CLICKHOUSE_USER")
CLICKHOUSE_PASSWORD = os.getenv("CLICKHOUSE_PASSWORD")

DATA_PATH = Path("data/processed")

# Establish connection
client = clickhouse_connect.get_client(
    host=CLICKHOUSE_HOST,
    port=CLICKHOUSE_PORT,
    username=CLICKHOUSE_USER,
    password=CLICKHOUSE_PASSWORD,
    database=CLICKHOUSE_DB
)

def load_dataframe_to_clickhouse(table_name: str, csv_file_path: Path):
    try:
        df = pd.read_csv(csv_file_path)

        if df.empty:
            print(f"{table_name} is empty, skipping...")
            return

        # Convert datetime-related columns
        if 'time_id' in df.columns:
            df['time_id'] = pd.to_datetime(df['time_id'])

        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date']).dt.date  # Ensure it's just a date, not datetime

        print(f"Loading {table_name} from {csv_file_path} with {len(df)} rows")
        client.insert_df(table_name, df)
        print(f"Successfully loaded {table_name}")
    except Exception as e:
        print(f"Failed to load {table_name}: {e}")

# Load all tables
load_dataframe_to_clickhouse("dim_user", DATA_PATH / "dim_user.csv")
load_dataframe_to_clickhouse("dim_course", DATA_PATH / "dim_course.csv")
load_dataframe_to_clickhouse("dim_time", DATA_PATH / "dim_time.csv")
load_dataframe_to_clickhouse("fact_enrollment", DATA_PATH / "fact_enrollment.csv")