STREAMING_DYNAMIC_TABLE_STATEMENTS = [
    "USE ROLE ACCOUNTADMIN",
    "USE DATABASE TRADING_ANALYTICS",
    "CREATE SCHEMA IF NOT EXISTS BRONZE",
    "CREATE SCHEMA IF NOT EXISTS SILVER",
    "CREATE SCHEMA IF NOT EXISTS GOLD",
    "CREATE TABLE IF NOT EXISTS BRONZE.TRADES_RAW (RECORD_METADATA VARIANT, RECORD_CONTENT VARIANT)",
    """
    CREATE OR REPLACE DYNAMIC TABLE SILVER.TRADES_CLEAN_DT
      TARGET_LAG = '60 seconds'
      WAREHOUSE = TRADING_WH
    AS
    WITH parsed AS (
      SELECT
        RECORD_CONTENT:e::string AS event_type,
        TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:E::string), 3) AS event_time,
        RECORD_CONTENT:s::string AS symbol,
        RECORD_CONTENT:t::number AS trade_id,
        TRY_TO_DECIMAL(RECORD_CONTENT:p::string, 38, 18) AS price,
        TRY_TO_DECIMAL(RECORD_CONTENT:q::string, 38, 18) AS quantity,
        RECORD_CONTENT:b::number AS buyer_order_id,
        RECORD_CONTENT:a::number AS seller_order_id,
        TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:T::string), 3) AS trade_time,
        RECORD_CONTENT:m::boolean AS is_maker,
        COALESCE(
          TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_METADATA:CreateTime::string), 3),
          TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_METADATA:createTime::string), 3),
          TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_METADATA:CREATETIME::string), 3),
          TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:E::string), 3),
          TO_TIMESTAMP_NTZ(TRY_TO_NUMBER(RECORD_CONTENT:T::string), 3)
        ) AS ingested_at
      FROM BRONZE.TRADES_RAW
    ),
    dedup AS (
      SELECT
        *,
        ROW_NUMBER() OVER (
          PARTITION BY symbol, trade_id
          ORDER BY ingested_at DESC
        ) AS rn
      FROM parsed
      WHERE symbol IS NOT NULL
        AND trade_id IS NOT NULL
        AND trade_time IS NOT NULL
        AND price IS NOT NULL
        AND quantity IS NOT NULL
    )
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
      DATE_TRUNC('day', trade_time)::date AS trade_date
    FROM dedup
    WHERE rn = 1
    """,
    """
    CREATE OR REPLACE DYNAMIC TABLE GOLD.TRADES_1M_DT
      TARGET_LAG = '60 seconds'
      WAREHOUSE = TRADING_WH
    AS
    SELECT
      symbol,
      DATE_TRUNC('minute', trade_time) AS minute_bucket,
      COUNT(*) AS trade_count,
      SUM(quantity) AS total_quantity,
      SUM(price * quantity) AS total_notional,
      AVG(price) AS avg_price,
      MIN(price) AS min_price,
      MAX(price) AS max_price,
      MIN(trade_time) AS first_trade_time,
      MAX(trade_time) AS last_trade_time
    FROM SILVER.TRADES_CLEAN_DT
    GROUP BY symbol, DATE_TRUNC('minute', trade_time)
    """,
]
