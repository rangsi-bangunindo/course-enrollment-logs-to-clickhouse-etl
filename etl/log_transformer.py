"""
This script reads semi-structured enrollment log data,
parses and normalizes it into 3 dimension tables and 1 fact table
based on the star schema defined in ClickHouse.

Input:  data/raw/enrollment_logs.txt
Output: CSVs in data/processed/:
    - dim_user.csv
    - dim_course.csv
    - dim_time.csv
    - fact_enrollment.csv
"""

import os
import csv
from datetime import datetime
from pathlib import Path

RAW_PATH = Path("data/raw/enrollment_logs.txt")
PROCESSED_DIR = Path("data/processed/")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Hold intermediate structured records
dim_users = {}
dim_courses = {}
dim_times = {}
fact_enrollments = []

# Read and parse each log entry
with RAW_PATH.open("r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        if not line:
            continue  # skip blank lines

        # Split log line
        timestamp_str, _, user_str, course_str, price_str = map(str.strip, line.split(" | "))

        # Extract time dimension
        time_id = datetime.strptime(timestamp_str, "%Y-%m-%dT%H:%M:%SZ")
        time_key = time_id.isoformat()
        if time_key not in dim_times:
            dim_times[time_key] = {
                "time_id": time_id,
                "date": time_id.date(),
                "year": time_id.year,
                "month": time_id.month,
                "day": time_id.day,
                "hour": time_id.hour
            }

        # Extract user dimension
        user_fields = dict(field.split("=") for field in user_str.split(";"))
        user_id = int(user_fields["user_id"])
        if user_id not in dim_users:
            dim_users[user_id] = {
                "user_id": user_id,
                "user_name": user_fields["user_name"],
                "user_city": user_fields["user_city"]
            }

        # Extract course dimension
        course_fields = dict(field.split("=") for field in course_str.split(";"))
        course_id = course_fields["course_id"]
        if course_id not in dim_courses:
            dim_courses[course_id] = {
                "course_id": course_id,
                "course_name": course_fields["course_name"],
                "category": course_fields["category"]
            }

        # Extract fact table
        price_parts = dict(field.split("=") for field in price_str.split(";"))
        price = int(price_parts["price"])
        promo_code = price_parts["promo_code"]
        if promo_code == "NULL":
            promo_code = None

        final_price = price if promo_code is None else None

        fact_enrollments.append({
            "time_id": time_id.isoformat(sep=" "),
            "user_id": user_id,
            "course_id": course_id,
            "price": price,
            "promo_code": promo_code,
            "final_price": final_price
        })

# Write to CSV files
def write_csv(file_path, fieldnames, rows):
    with open(file_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

write_csv(PROCESSED_DIR / "dim_user.csv", ["user_id", "user_name", "user_city"], dim_users.values())
write_csv(PROCESSED_DIR / "dim_course.csv", ["course_id", "course_name", "category"], dim_courses.values())
write_csv(PROCESSED_DIR / "dim_time.csv", ["time_id", "date", "year", "month", "day", "hour"], dim_times.values())
write_csv(PROCESSED_DIR / "fact_enrollment.csv",
          ["time_id", "user_id", "course_id", "price", "promo_code", "final_price"],
          fact_enrollments)