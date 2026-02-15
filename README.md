# Crypto Trading ELT Real Time Pipeline

[![Trading Data Pipeline](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml)

> Build a production-style ELT streaming platform that ingests Binance trades in real time and serves curated analytics in Snowflake.

### No UI Clicks ever.

<b>Everything</b> is configured through code: infrastructure, ingestion, orchestration, and transformations.

- **Binance WebSocket** (trade source)
- **Kafka + Kafka Connect** (stream transport and Snowflake sink)
- **Airflow** (orchestration)
- **Snowflake Dynamic Tables** (Silver and Gold transformations)
- **Snowflake** (analytics warehouse)

## You do not scale one pipeline. You scale a pattern

This project is organized to ingest trading data continuously and answer analytics questions such as:

- Is the stream healthy and fresh right now?
- How many trades and notional volume are observed per minute?
- Are Silver/Gold transformations up to date and deduplicated?

The environment is reproducible locally with a clear `make` workflow.

## Quickstart (Makefile)

```bash
# Full setup from scratch (new machine / new Snowflake account)
make setup.from-scratch

# Full runtime infra from scratch (airflow + kafka/connect + sink + websocket)
make infra.from-scratch

# Start only Airflow
make infra.up

# Start full runtime infra
make infra.up-all

# Stop local containers
make infra.down

# List all commands
make help
```

```yml
setup.from-scratch execution

Check local dependencies
   │
   ▼
Generate .env
   │
   ▼
Provision Snowflake resources via Terraform
   │
   ▼
Generate Snowflake key-pair auth
   │
   ▼
Create streaming Dynamic Tables
   │
   ▼
Ready to run full local streaming stack
```

---

## Airflow Orchestration

### Streaming Operations DAGs

Airflow orchestrates runtime operations for the streaming pipeline:

```yml
bootstrap_streaming_stack (manual)
  configure Snowflake sink connector
  apply Dynamic Table definitions

streaming_healthcheck (every 5 min)
  connector status check
  bronze/silver freshness checks

streaming_data_quality (every 15 min)
  not-null checks
  duplicate checks
  recent activity checks

streaming_cost_governance (hourly)
  warehouse guardrails
  credit threshold signal

streaming_ops_report (daily 09:00)
  operational summary

streaming_backfill (manual)
  rebuild Silver/Gold from Bronze history

streaming_recovery (manual)
  recover connector and validate freshness
```

---

Airflow owns **execution**, not business logic.

```python
with DAG(
    dag_id="streaming_healthcheck",
    ...
) as dag:
    connector_health = PythonOperator(
        task_id="check_connector_status",
        ...
    )

    freshness = PythonOperator(
        task_id="check_streaming_freshness",
        ...
    )

    connector_health >> freshness
```

## Configuration-driven Philosophy

> **Inform credentials once. Build and run everything from code.**

- Infrastructure via Terraform
- Connector provisioning and updates via scripts/Airflow service layer
- Local environment lifecycle managed with `make`
- No manual Airflow configuration steps for core flow
- No manual Snowflake object creation

The system is **configuration-driven**: changing sources or targets is a controlled code change.

---

## High-Level Architecture

```yml
Binance WebSocket Producer  ──────────────┐
   │                                      │
   │ trade events (JSON)                  │
   ▼                                      │
Kafka topic (crypto_trades)               │
   │                                      │
   ▼                                      │
Kafka Connect Snowflake Sink ─────────────┼──► Snowflake BRONZE.TRADES_RAW
                                          │
Airflow Orchestrator ─────────────────────┤
  - healthcheck                           │
  - quality                               │
  - governance / reporting / recovery     │
                                          │
Snowflake Dynamic Tables                  │
  - SILVER.TRADES_CLEAN_DT                │
  - GOLD.TRADES_1M_DT                     │
                                          │
BI / Analytics  ◄─────────────────────────┘
```

---

## Continuous integration Flow

[![Trading Data Pipeline](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml)

```bash
Steps

Lint Check (Ruff)  ─────┐
Format Check (Black)    │
Airflow DAG Import Test ┼──► GitHub Actions
                        │
Quality Gate Passed ────┘
```

---

## Ingestion Details

- Binance WebSocket producer publishes trades to Kafka (`crypto_trades`)
- Snowflake Kafka Sink writes raw payload into `TRADING_ANALYTICS.BRONZE.TRADES_RAW`
- Dynamic Table `SILVER.TRADES_CLEAN_DT` parses/casts/deduplicates the stream
- Dynamic Table `GOLD.TRADES_1M_DT` computes 1-minute aggregates for analytics

---

## Snowflake via Terraform

Snowflake resources are provisioned and managed by Terraform, including:

- Warehouse configuration
- Role and grants management
- Database and schema setup for Bronze/Silver/Gold layers

```yml
infra/remote/snowflake/
├── setup/
│   ├── generate_terraform_user.sh
│   ├── install_local_cli.sh
│   ├── roles.sql
│   └── streaming/
│       ├── 00_create_schemas.sql
│       ├── 10_silver_trades_clean_dt.sql
│       └── 20_gold_trades_1m_dt.sql
│
├── warehouse.tf
├── grants.tf
├── main.tf
├── provider.tf
├── variables.tf
└── versions.tf
```

---

## Local Infra

```yml
infra/local
├── airflow/
├── kafka-connect/
└── websocket/
```

### Kafka Connect flow

```yml
make infra.start-kafka-connect
   │
   ▼
Start Zookeeper + Kafka + Kafka Connect
   │
   ▼
make infra.configure-snowflake-kafka-sink
   │
   ▼
Connector snowflake-trades-sink writes to BRONZE.TRADES_RAW
```

### Full runtime flow

```yml
make infra.up-all
   │
   ├── start Airflow stack
   ├── start Kafka + Connect stack
   ├── configure Snowflake sink
   └── start websocket producer container
```

### Airflow orchestrator

```yml
Container starts  ──────────────┐
   │                            │
   ▼                            │
Load DAGs                       │
   ├── Bootstrap/Recovery       │
   ├── Healthcheck/Quality      │
   └── Governance/Reporting     │
   ▼                            │
Streaming operations ready ◄────┘
```

## Trading Business Questions

The pipeline is designed to answer practical streaming questions, such as:

- Is ingestion live right now, or stalled?
- What is trade activity by symbol per minute?
- How fast is Silver/Gold refresh relative to incoming trades?
- Are there data quality issues (nulls, duplicates, inactivity)?
