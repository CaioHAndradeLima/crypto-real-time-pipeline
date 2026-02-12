# Kafka Connect + Snowflake Sink (Local)

This stack starts:

- Kafka broker (`localhost:9092`)
- Kafka Connect REST API (`localhost:8083`)
- Snowflake Kafka Sink plugin (installed on startup)

## Required `.env` variables

- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PRIVATE_KEY` (Snowflake private key, base64 DER for key-pair auth)
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_ROLE`

Optional with defaults:

- `SNOWFLAKE_WAREHOUSE` (default: `TRADING_WH`)
- `KAFKA_TOPIC_TRADES` (default: `crypto_trades`)
- `SNOWFLAKE_SCHEMA` (must be `BRONZE`; default: `BRONZE`)
- `SNOWFLAKE_TRADES_RAW_TABLE` (must be `TRADES_RAW`; default: `TRADES_RAW`)
- `SNOWFLAKE_PRIVATE_KEY_PASSPHRASE` (optional, if key is encrypted)
- `SNOWFLAKE_ACCOUNT_IDENTIFIER` (optional override; default: `<ORG>-<ACCOUNT>`)
- `SNOWFLAKE_URL_NAME` (optional override; default: `<ACCOUNT_IDENTIFIER>.snowflakecomputing.com`)

## Commands

```bash
make infra.start-kafka-connect
make infra.configure-snowflake-kafka-sink
```
