from airflow import DAG
from airflow.operators.empty import EmptyOperator
from dotenv import load_dotenv

from src.ingestion.airbyte.tasks import list_connections
from src.ingestion.airbyte.task_groups import airbyte_connection_group
from src.lineage.datasets import TRADING_BRONZE, TRADING_INGESTION

load_dotenv()

from airflow.datasets import Dataset
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from datetime import datetime, timedelta

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="postgres_to_snowflake_bronze",
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["bronze", "airbyte"],
    schedule=[TRADING_INGESTION],
    max_active_tasks=1,
    default_args=DEFAULT_ARGS,
) as dag:

    connections = list_connections()

    mapped_airbyte_group = airbyte_connection_group.expand_kwargs(connections)

    publish_dataset = EmptyOperator(
        task_id="publish_trading_bronze",
        outlets=[TRADING_BRONZE],
    )

    mapped_airbyte_group >> publish_dataset
