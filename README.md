# NYC Trading ELT Pipeline (NOAA)

[![Trading Data Pipeline](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml)

> Build a production-style ELT platform that ingests NOAA trading observations for New York City and delivers monthly rainfall indicators in Snowflake.

### No UI Clicks ever.

<b>Everything</b> is configured through code: infrastructure, ingestion, orchestration, and transformations.

- **NOAA** (trading source for NYC observations)
- **Airbyte** (connector-based ingestion flows)
- **Airflow** (orchestration)
- **dbt** (Silver and Gold transformations)
- **Snowflake** (analytics warehouse)

## You do not scale one pipeline. You scale a pattern

This project is organized to ingest trading data continuously and answer analytics questions such as:

- How many days did it rain in New York City each month?
- What was total monthly precipitation in NYC?
- Which periods are getting wetter or drier over time?

The environment is reproducible locally with a clear `make` workflow.

## Quickstart (Makefile)

```bash
# 1) create .env with Snowflake credentials and local settings
make setup.create-env

# 2) provision Snowflake resources via Terraform
make setup.provision-snowflake

# 3) generate dbt profile from .env
make setup.configure-dbt-profile

# optional: run the full setup chain
make setup.local-development-environment

# start/stop local services
make infra.up
make infra.down

# inspect all commands
make help
```

```yml
setup.local-development-environment execution

Collect Snowflake credentials and generate .env
   │
   ▼
Provision Snowflake resources via Terraform
   │
   ▼
Generate dbt profiles.yml
   │
   ▼
Ready to start local infra and run NYC trading pipelines
```

---

## Airflow Orchestration

### Data-Driven Orchestration for NOAA Ingestion

**Conceptual flow:**

```yml
    DAG started
        │
        ▼
trigger NOAA ingestion to BRONZE
        │
        ▼
validate ingestion completion
        │
        ▼
run dbt SILVER models
        │
        ▼
run dbt GOLD models (monthly rain indicators)
```

---

Airflow owns **execution**, not business logic.

```python
with DAG(
    dag_id="noaa_to_snowflake_bronze",
    ...
) as dag:
    ingest = PythonOperator(
        task_id="ingest_noaa_observations",
        ...
    )

    silver = EmptyOperator(task_id="Trigger_DBT_Silver")
    gold = EmptyOperator(task_id="Trigger_DBT_Gold")

    ingest >> silver >> gold
```

### Airflow Graph

![img.png](.images/airflow_graph.png)

## Configuration-driven Philosophy

> **Inform credentials once. Build and run everything from code.**

- Infrastructure via Terraform
- Ingestion orchestrated programmatically
- Local environment lifecycle managed with `make`
- No manual Airflow configuration steps for core flow
- No manual Snowflake object creation

The system is **configuration-driven**: changing sources or targets is a controlled code change.

---

## High-Level Architecture

```yml
NOAA Source (NYC)  ───────────┐
   │                          │
   │  Trading observations    │
   ▼                          │
Ingestion Layer               │
   │                          │
   │  Load raw data           │
   ▼                          ┼──► Airflow Orchestrator
Snowflake                     │
   ├── BRONZE                 │
   ├── SILVER                 │
   └── GOLD                   │
   │                          │
   ▼                          │
BI / Analytics  ◄─────────────┘
```

---

## Continuous integration Flow

[![Trading Data Pipeline](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml)

```bash
Steps

Lint Check  ────────────┐
   ├── Ruff             │
   │                    │
   ▼                    │
Formatting Check        │
   ├── Black            │
   │                    │
   ▼                    │
Validate DAG imports    │
   ├── Airflow          ┼──► GitHub Actions
   │                    │
   ▼                    │
Validate dbt            │
   ├── SILVER           │
   └── GOLD             │
   │                    │
   ▼                    │
Analytics Ready ────────┘
```

---

## Ingestion Details

- NOAA observations are ingested for New York City
- Raw data lands in **BRONZE**
- dbt models standardize and enrich in **SILVER**
- Business metrics are published in **GOLD**

---

## Snowflake via Terraform

Snowflake resources are provisioned and managed by Terraform, including:

- Warehouse configuration
- Role and grants management
- Database and schema setup for dbt layers

```yml
infra/remote/snowflake/
├── setup/
│   ├── generate_terraform_user.sh
│   ├── install_local_cli.sh
│   └── roles.sql
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
├── postgres/
├── airbyte/
└── airflow/
```

### Postgres configuration-driven flow

```yml
└── init/
    ├── 01_wal_level_setup.sql   # Logical replication settings
    ├── 02_init_retail_oltp.sql  # Local source schema bootstrap (legacy filename)
    ├── 03_cdc.sql               # CDC support
    └── 05_airbyte_user.sql      # Airbyte user and grants
```

### Airbyte configuration-driven flow

```yml
start_airbyte.sh             ──────────────┐
   ├── Start Airbyte local stack           │
   │                                       │
   ▼                                       │
setup_credentials.sh                       │
setup_postgres_source.sh                   │
setup_snowflake_destination.sh             │
generate_ingestion_json.sh                 │
create_connections.sh                      │
   │                                       │
   ▼                                       │
Start Airflow  ◄───────────────────────────┘
```

### Airflow orchestrator

```yml
Container starts  ──────────────┐
   │                            │
   ▼                            │
Load DAGs                       │
   ├── Bronze ingestion         │
   ├── Silver transformation    │
   └── Gold transformation      │
   ▼                            │
NYC trading metrics ready ◄─────┘
```

## Trading Business Questions

The pipeline is designed to answer trading analytics questions for New York City, such as:

- How many days did it rain in NYC per month?
- What is total monthly precipitation in NYC?
- How does rainfall vary by season?
- Which months are above historical rainfall average?

## dbt Strategy

dbt is executed via **CLI orchestration**, intentionally simple:

| Approach         | Reason                     |
|------------------|----------------------------|
| CLI-based dbt    | Low complexity, easy CI/CD |
| No Cosmos        | Avoid DAG explosion        |
| Layer-level runs | Clear failure domains      |

---
