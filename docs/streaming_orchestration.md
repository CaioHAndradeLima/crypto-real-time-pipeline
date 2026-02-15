# Streaming Orchestration Strategy

## Runtime services (continuous)

- `local-binance-ws-producer`: reads Binance WebSocket and publishes to Kafka.
- `local-kafka`: streaming buffer.
- `local-kafka-connect`: Snowflake sink connector.
- Snowflake Dynamic Tables:
  - `TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT`
  - `TRADING_ANALYTICS.GOLD.TRADES_1M_DT`

These are always-on components. They are not batch jobs.

## Airflow role (control-plane)

Airflow should orchestrate operations around the stream, not individual records.

### `bootstrap_streaming_stack` (manual)

1. Configure Snowflake Kafka sink connector (`snowflake-trades-sink`).
2. Create or replace streaming Dynamic Tables (silver and gold).

### `streaming_healthcheck` (every 5 minutes)

1. Verify connector and task states are `RUNNING`.
2. Verify bronze has recent rows (`last 5 minutes`).
3. Verify silver lag is acceptable.

If any check fails, the DAG fails and triggers alerting policies.

### Additional operational DAGs

- `streaming_data_quality` (every 15 minutes): null, duplicate, and activity checks.
- `streaming_recovery` (manual): connector recovery and post-recovery validation.
- `streaming_backfill` (manual): rebuild dynamic tables from bronze history.
- `streaming_cost_governance` (hourly): enforce warehouse autosuspend/autoresume and credit guardrail.
- `streaming_ops_report` (daily): send summary metrics.

## Slack failure alerts

Set `SLACK_WEBHOOK_URL` in `.env`.  
All streaming DAG tasks use an `on_failure_callback` that sends failure details to Slack.

## Local startup commands

```bash
make infra.up-all
```

This starts airflow + kafka connect stack + connector config + websocket producer.
