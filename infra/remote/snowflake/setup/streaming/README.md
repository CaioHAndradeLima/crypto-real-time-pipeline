# Streaming Transformation Layout

This folder defines the Snowflake streaming transformation layer in ordered steps:

- `00_create_schemas.sql`: create `SILVER` and `GOLD` schemas.
- `10_silver_trades_clean_dt.sql`: create `SILVER.TRADES_CLEAN_DT` dynamic table (parse, cast, dedupe).
- `20_gold_trades_1m_dt.sql`: create `GOLD.TRADES_1M_DT` dynamic table (1-minute aggregates).

Execution order is lexical (`00`, `10`, `20`) and is handled by:

```bash
make infra.create-streaming-dynamic-tables
```
