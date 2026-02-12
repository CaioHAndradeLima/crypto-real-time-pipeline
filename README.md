# Weather Data Pipeline

[![Weather Data Pipeline](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml)

> Generate a production‑grade, data‑driven ELT platform built from scratch only passing your snowflake credentials using
> `make setup`.

### No UI Clicks ever.

<b>Everything</b> — sources, destinations, connections, syncs, and transformations — **is created programmatically**.

- **Postgres** (OLTP Production data source)
- **Airbyte** (ingestion + CDC)
- **Airflow** (orchestration & lineage)
- **dbt** (Silver & Gold transformations)
- **Snowflake** (Lakehouse + Medallion Architecture)

## You don’t scale pipelines. You scale patterns

You will generate your entire infra, <b>capable of deal 10 thousand new tables</b>, including all ingestion
configuration between production source and Snowflake/Bronze, <b>without any effort</b>. You only need run `make setup`.

## Quickstart (Makefile)

```bash
# install python dependencies
make bootstrap

# full setup (creates .env, provisions Snowflake, starts local infra)
make setup

# manage local services
make up
make down

# inspect available commands
make help
```

``` yml
make setup execution

Collect your Snowflake credentials and save into .env
   │
   ▼
Create all Snowflake remote infrastructure via Terraform
   │
   ▼
Start Postgres db simulating real production environment 
(Replace with real db info if you have one)
   │
   ▼
Start Airbyte and connect with Postgres and Snowflake
   │
   ▼
Discovers Postgres tables automatically and generate a ingestion.json
   │
   ▼
Create all ingestion connection between Postgres-Snowflake based on ingestion.json
   │
   ▼
Start Airflow and add Airbyte as a new connection
   │
   ▼
Bronze/Silver/Gold DAG is ready to run
```
---

## Airflow Orchestration

### Data‑Driven Orchestration through Dynamic Airbyte Ingestion


**Conceptual flow:**

``` yml
    DAG started
        │
        ▼
recover airbyte connections
  tables/columns to sync 
        │
        ▼
[ trigger_connection_1 ]──sensor results──┐
[ trigger_connection_2 ]──sensor results──┼──► trigger_dbt_silver
[ trigger_connection_3 ]──sensor results──┘            │
                                                       ▼
                                                 trigger_dbt_gold
```


---


Airflow owns **execution**, not configuration.


```python
with DAG(
    dag_id="postgres_to_snowflake_bronze",
    ...
) as dag:

    # Discover automatically connections from Airbyte HTTP API
    connections = discover_connections(client, tables)

    # start ingestion sync of raw layer from postgres -> snowflake
    sync = AirbyteTriggerSyncOperator(
        task_id="sync_airbyte_connection",
        pool="airbyte_sequential",
        ...
    )

    # Keep listening ingestion success from Airbyte api
    sensor = AirbyteJobSensor(
        task_id="sensor_airbyte_connection",
        airbyte_job_id=sync.output,
        pool="airbyte_sequential",
        ...
    )

    # Start Silver dbt 
    end = EmptyOperator(
        task_id="Trigger_DBT_Silver",
        outlets=[WEATHER_BRONZE],
    )
```
### Airflow Graph

![img.png](.images/airflow_graph.png)

## Configuration-driven Philosophy

> **You inform your Snowflake account once. The platform builds itself through setup script.**

- Discovers Airbyte connections programmatically
- Triggers all connections in parallel
- Waits for completion via sensors
- No manual Airbyte UI configuration
- No manual Airflow UI configuration
- No manual Bronze/Raw configuration.
- No more dags to add new tables.
- No hardcoded pipelines per table
- No fragile point‑to‑point DAGs
- No ingestion headaches.
- No dbt Bronze models are required (only for testing)

The system is **data‑driven**: adding a table is a configuration change, not a new pipeline.

---

## High‑Level Architecture

``` yml
Postgres (OLTP)  ───────────┐
   │                        │
   │  CDC / Incremental     │
   ▼                        │
Airbyte (API‑driven)        │
   │                        │
   │  Bulk load + dedup     │
   ▼                        ┼──► Airbyte Orchestrator
Snowflake                   │
   ├── BRONZE               │
   ├── SILVER               │
   └── GOLD                 │
   │                        │
   ▼                        │
BI / Analytics  ◄───────────┘
```

---
## Continuous integration Flow

[![Weather Data Pipeline](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml/badge.svg)](https://github.com/CaioHAndradeLima/retail-data-pipeline/actions/workflows/ci.yml)

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
Validate Dag imports    │
   ├── Airflow          ┼──► Github Actions
   │                    │
   ▼                    │
Validate DBT            │
   ├── SILVER           │
   └── GOLD             │
   │                    │
   ▼                    │
BI / Analytics  ────────┘
```

---

## Ingestion Details

- Postgres tables are ingested via **Airbyte**
- Mix of **CDC** and **incremental batch**
- Deduplication handled by Airbyte (`append_dedup`)

---

## Snowflake via Terraform

All Snowflake structure is defined by Terraform Architecture, including:

- Configure warehouses
- Manage roles, grants, and permissions
- Prepare the environment for dbt transformations

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
├── postgres/               # Airbyte ingestion tool directory
├── airbyte/                # Airbyte ingestion tool directory
├── airflow/                # Orchestrator directory
|
├── start_containers.sh     # Used by `make up`
├── stop_containers.sh      # Used by `make down`
```


### Postgres configuration-driven flow

```yml
└── init/
    ├── 01_wal_level_setup.sql  # SET wal_level = logical;
    │                                        
    ├── 02_init_retail_oltp.sql # Create tables
    │
    ├── 03_data.sql             # Populate tables with fake data
    │                                        
    ├── 04_cdc.sql              # Enable CDC replication
    │                                        
    └── 05_airbyte_user.sql     # Create CDC Airbyte User
```

### Airbyte configuration-driven flow

```yml
brew_install_airbyte_abctl.sh  ─────────────┐
   ├── Install Airbyte via abctl            │
   │                                        │
   ▼                                        │
setup_credentials.sh                        │
   ├── Setup email/organizaton data         │
   │                                        │
   ▼                                        │
setup_postgres_source.sh                    │
   ├── Add source connection                │
   │                                        │
   ▼                                        │
setup_snowflake_destination.sh              │
   ├── Add Snowflake connection             │
   │                                        │
   ▼                                        │
generate_ingestion.json.sh                  │
   ├── Read Postgres Source                 │
   └── Create ingestion tables/connections  │
   └── insert into ingestion.json           │
   │                                        │
   ▼                                        │
create_connections.sh                       │
   ├── Read ingestion.json                  │
   ├── Architecture ingestion connection    │
   ├── Add or update all ingestion process  │
   │                                        │
   ▼                                        │
Start Airflow  ◄────────────────────────────┘
```

### Airflow orchestrator

```yml
Container starts  ──────────────┐
   │                            │
   ▼                            │
init_connections.sh             │
   ├── add airbyte connection   │
   │                            │
   ▼                            │
Start Weather Pipeline           │
   ├── Bronze                   │
   ├── Silver                   │
   ├── Gold                     │
   ▼                            │
Data Available  ◄───────────────┘
```

## Weather Business Questions

The postgres used has tables and data designed to answer typical retail business questions such as:

- How many orders are created per day?
- How much revenue is generated?
- What is the order conversion rate?
- Which products generate the most revenue?
- What percentage of orders are canceled or refunded?
- How long does it take for an order to move from created from shipped to delivered?

CDC is enabled for the `orders` table in the OLTP database. All other tables are ingested using a batch approach.


## dbt Strategy

dbt is executed via **CLI orchestration**, intentionally simple:

| Approach         | Reason                     |
|------------------|----------------------------|
| CLI‑based dbt    | Low complexity, easy CI/CD |
| No Cosmos        | Avoid DAG explosion        |
| Layer‑level runs | Clear failure domains      |

---
