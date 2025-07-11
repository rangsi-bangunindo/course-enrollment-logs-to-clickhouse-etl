-- Creates normalized dimensional tables and fact table in ClickHouse
-- using Star Schema design for analyzing course enrollment logs.
-- This version applies best practices in data type selection, optimization,
-- and table-level configurations.

-- DIMENSION TABLE: dim_user
-- Stores unique user information
CREATE TABLE IF NOT EXISTS dim_user (
    user_id UInt64,                                      -- Primary identifier for user
    user_name String,                                    -- Full user name (not normalized further)
    user_city LowCardinality(String)                     -- City name: low cardinality, good compression
)
ENGINE = MergeTree()
ORDER BY user_id;

-- DIMENSION TABLE: dim_course
-- Stores unique course metadata
CREATE TABLE IF NOT EXISTS dim_course (
    course_id LowCardinality(String),                    -- Short course ID (e.g., "C-01")
    course_name String,                                  -- Course title
    category LowCardinality(String)                      -- Field/category: e.g., "Pemrograman", "Bisnis"
)
ENGINE = MergeTree()
ORDER BY course_id;

-- DIMENSION TABLE: dim_time
-- Stores timestamp breakdown for time-based analysis
CREATE TABLE IF NOT EXISTS dim_time (
    time_id DateTime,                                    -- Full timestamp (acts as primary key)
    date Date,                                           -- Date only (for calendar joins)
    year UInt16,
    month UInt8,
    day UInt8,
    hour UInt8
)
ENGINE = MergeTree()
ORDER BY time_id;

-- FACT TABLE: fact_enrollment
-- Core table capturing enrollment transactions
CREATE TABLE IF NOT EXISTS fact_enrollment (
    -- Foreign keys (dimensions)
    time_id DateTime,                                    -- UTC timestamp of enrollment
    user_id UInt64,                                      -- FK to dim_user
    course_id LowCardinality(String),                    -- FK to dim_course
    -- Measures
    price UInt32,                                        -- Original course price (full price) in IDR
    promo_code LowCardinality(Nullable(String)),         -- Promo code used, if any
    final_price Nullable(UInt32)                         -- Future use: NULL if discount exists, otherwise = price
)
ENGINE = MergeTree()
PARTITION BY toYYYYMM(time_id)                           -- Monthly partitions for log-based growth
ORDER BY (course_id, time_id, user_id);                  -- Optimized for queries by course and time window