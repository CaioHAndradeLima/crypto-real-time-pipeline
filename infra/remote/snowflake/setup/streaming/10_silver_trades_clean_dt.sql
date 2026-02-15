-- Use privileged context for object creation in this setup script.
USE ROLE ACCOUNTADMIN;
USE DATABASE TRADING_ANALYTICS;
USE SCHEMA SILVER;

-- Silver layer dynamic table:
-- Parses raw Kafka payload, enforces data types, and removes duplicates.
CREATE OR REPLACE DYNAMIC TABLE SILVER.TRADES_CLEAN_DT
  -- Freshness target. Snowflake tries to keep this table within ~60s of source changes.
  TARGET_LAG = '60 seconds'
  -- Warehouse used by Snowflake to refresh this dynamic table.
  WAREHOUSE = TRADING_WH
AS
-- Step 1: parse raw variant payload into typed columns.
WITH parsed AS (
  SELECT
    -- Binance event type ("trade")
    RECORD_CONTENT:e::string AS event_type,
    -- Event time in epoch milliseconds -> timestamp_ntz
    TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:E::string), 3) AS event_time,
    RECORD_CONTENT:s::string AS symbol,
    RECORD_CONTENT:t::number AS trade_id,
    -- Price/quantity arrive as strings in Binance payload.
    TRY_TO_DECIMAL(RECORD_CONTENT:p::string, 38, 18) AS price,
    TRY_TO_DECIMAL(RECORD_CONTENT:q::string, 38, 18) AS quantity,
    RECORD_CONTENT:b::number AS buyer_order_id,
    RECORD_CONTENT:a::number AS seller_order_id,
    -- Trade execution time in epoch milliseconds -> timestamp_ntz
    TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:T::string), 3) AS trade_time,
    RECORD_CONTENT:m::boolean AS is_maker,
    -- Best-effort ingestion timestamp:
    -- prefer connector metadata when present, fallback to event/trade times.
    COALESCE(
      TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_METADATA:CreateTime::string), 3),
      TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_METADATA:createTime::string), 3),
      TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_METADATA:CREATETIME::string), 3),
      TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:E::string), 3),
      TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:T::string), 3)
    ) AS ingested_at
  FROM BRONZE.TRADES_RAW
),
-- Step 2: deduplicate by natural key (symbol + trade_id).
-- Keep latest ingestion when duplicates exist.
dedup AS (
  SELECT
    *,
    ROW_NUMBER() OVER (
      PARTITION BY symbol, trade_id
      ORDER BY ingested_at DESC
    ) AS rn
  FROM parsed
  -- Basic data quality filter to keep only valid rows.
  WHERE symbol IS NOT NULL
    AND trade_id IS NOT NULL
    AND trade_time IS NOT NULL
    AND price IS NOT NULL
    AND quantity IS NOT NULL
)
-- Step 3: final silver projection.
SELECT
  event_type,
  event_time,
  symbol,
  trade_id,
  price,
  quantity,
  buyer_order_id,
  seller_order_id,
  trade_time,
  is_maker,
  ingested_at,
  -- Partition/helper column for downstream aggregations and pruning.
  DATE_TRUNC('day', trade_time)::date AS trade_date
FROM dedup
WHERE rn = 1;
