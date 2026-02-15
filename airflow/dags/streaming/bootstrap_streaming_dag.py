import json
import os
from datetime import datetime
from urllib.request import Request, urlopen

import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
}


def configure_connector() -> None:
    connect_url = os.getenv("CONNECT_URL", "http://host.docker.internal:8083")
    connector_name = os.getenv("CONNECTOR_NAME", "snowflake-trades-sink")
    topic_name = os.getenv("KAFKA_TOPIC_TRADES", "crypto_trades")
    warehouse = os.getenv("SNOWFLAKE_WAREHOUSE", "TRADING_WH")
    schema = os.getenv("SNOWFLAKE_SCHEMA", "BRONZE")
    table = os.getenv("SNOWFLAKE_TRADES_RAW_TABLE", "TRADES_RAW")
    account_identifier = os.getenv(
        "SNOWFLAKE_ACCOUNT_IDENTIFIER",
        f"{os.environ['SNOWFLAKE_ORGANIZATION_NAME']}-{os.environ['SNOWFLAKE_ACCOUNT']}",
    )
    snowflake_url = os.getenv(
        "SNOWFLAKE_URL_NAME",
        f"{account_identifier}.snowflakecomputing.com",
    )

    payload = {
        "connector.class": "com.snowflake.kafka.connector.SnowflakeSinkConnector",
        "tasks.max": "1",
        "topics": topic_name,
        "snowflake.url.name": snowflake_url,
        "snowflake.user.name": os.environ["SNOWFLAKE_USER"],
        "snowflake.private.key": os.environ["SNOWFLAKE_PRIVATE_KEY"],
        "snowflake.private.key.passphrase": os.getenv("SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", ""),
        "snowflake.database.name": os.environ["SNOWFLAKE_DATABASE"],
        "snowflake.schema.name": schema,
        "snowflake.role.name": os.environ["SNOWFLAKE_ROLE"],
        "snowflake.warehouse.name": warehouse,
        "snowflake.ingestion.method": "SNOWPIPE_STREAMING",
        "buffer.count.records": "1000",
        "buffer.flush.time": "10",
        "buffer.size.bytes": "5000000",
        "key.converter": "org.apache.kafka.connect.storage.StringConverter",
        "value.converter": "org.apache.kafka.connect.json.JsonConverter",
        "value.converter.schemas.enable": "false",
        "snowflake.topic2table.map": f"{topic_name}:{table}",
        "errors.tolerance": "all",
        "errors.log.enable": "true",
    }

    req = Request(
        f"{connect_url}/connectors/{connector_name}/config",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="PUT",
    )
    with urlopen(req, timeout=30) as response:
        if response.status // 100 != 2:
            raise RuntimeError(f"Connector configure failed with status {response.status}")


def apply_dynamic_tables() -> None:
    conn = snowflake.connector.connect(
        account=f"{os.environ['SNOWFLAKE_ORGANIZATION_NAME']}-{os.environ['SNOWFLAKE_ACCOUNT']}",
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ.get("SNOWFLAKE_DATABASE", "TRADING_ANALYTICS"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "BRONZE"),
    )
    statements = [
        "USE ROLE ACCOUNTADMIN",
        "USE DATABASE TRADING_ANALYTICS",
        "CREATE SCHEMA IF NOT EXISTS SILVER",
        "CREATE SCHEMA IF NOT EXISTS GOLD",
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
    try:
        with conn.cursor() as cur:
            for statement in statements:
                cur.execute(statement)
    finally:
        conn.close()


with DAG(
    dag_id="bootstrap_streaming_stack",
    description="Initialize connector and dynamic tables",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["streaming", "ops", "bootstrap"],
    is_paused_upon_creation=False,
) as dag:
    configure_sink = PythonOperator(
        task_id="configure_snowflake_kafka_sink",
        python_callable=configure_connector,
    )

    apply_dynamic_table_defs = PythonOperator(
        task_id="apply_dynamic_table_definitions",
        python_callable=apply_dynamic_tables,
    )

    configure_sink >> apply_dynamic_table_defs
