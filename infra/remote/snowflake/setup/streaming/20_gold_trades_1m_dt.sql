USE ROLE ACCOUNTADMIN;
USE DATABASE TRADING_ANALYTICS;
USE SCHEMA GOLD;

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
GROUP BY symbol, DATE_TRUNC('minute', trade_time);
