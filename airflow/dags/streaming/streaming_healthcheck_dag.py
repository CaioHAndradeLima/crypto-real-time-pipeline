import json
import os
from datetime import datetime, timedelta
from urllib.request import urlopen

import snowflake.connector
from airflow import DAG
from airflow.operators.python import PythonOperator

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}


def check_connector_status() -> None:
    connect_url = os.getenv("CONNECT_URL", "http://host.docker.internal:8083")
    connector = os.getenv("CONNECTOR_NAME", "snowflake-trades-sink")
    status_url = f"{connect_url}/connectors/{connector}/status"

    with urlopen(status_url, timeout=10) as response:
        payload = json.loads(response.read().decode("utf-8"))

    connector_state = payload.get("connector", {}).get("state")
    if connector_state != "RUNNING":
        raise RuntimeError(f"Connector state is {connector_state}, expected RUNNING")

    tasks = payload.get("tasks", [])
    if not tasks:
        raise RuntimeError("Connector has no running tasks")
    for task in tasks:
        if task.get("state") != "RUNNING":
            raise RuntimeError(f"Connector task not running: {task}")


def check_streaming_freshness() -> None:
    conn = snowflake.connector.connect(
        account=f"{os.environ['SNOWFLAKE_ORGANIZATION_NAME']}-{os.environ['SNOWFLAKE_ACCOUNT']}",
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        role=os.environ["SNOWFLAKE_ROLE"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
        database=os.environ.get("SNOWFLAKE_DATABASE", "TRADING_ANALYTICS"),
        schema=os.environ.get("SNOWFLAKE_SCHEMA", "BRONZE"),
    )
    try:
        with conn.cursor() as cur:
            # Bronze should be receiving rows recently when websocket producer is healthy.
            cur.execute(
                """
                select count(*) as recent_rows
                from TRADING_ANALYTICS.BRONZE.TRADES_RAW
                where to_timestamp_ntz(record_content:T::number, 3) >= dateadd('minute', -5, current_timestamp())
                """
            )
            recent_rows = cur.fetchone()[0]
            if recent_rows is None or recent_rows <= 0:
                raise RuntimeError("No recent rows in BRONZE.TRADES_RAW for last 5 minutes")

            # Silver must be refreshing and close to current time.
            cur.execute(
                """
                select datediff(
                  'second',
                  max(ingested_at),
                  current_timestamp()
                ) as lag_seconds
                from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
                """
            )
            lag_seconds = cur.fetchone()[0]
            if lag_seconds is None or lag_seconds > 600:
                raise RuntimeError(f"Silver lag too high: {lag_seconds} seconds")
    finally:
        conn.close()


with DAG(
    dag_id="streaming_healthcheck",
    description="Monitor connector and streaming freshness",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    tags=["streaming", "ops", "monitoring"],
    is_paused_upon_creation=False,
) as dag:
    connector_health = PythonOperator(
        task_id="check_connector_status",
        python_callable=check_connector_status,
    )

    freshness = PythonOperator(
        task_id="check_streaming_freshness",
        python_callable=check_streaming_freshness,
    )

    connector_health >> freshness
