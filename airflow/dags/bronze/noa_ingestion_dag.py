from airflow.datasets import Dataset
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from src.ingestion.noaa.noaa_observations_ingest import ingest_noaa_observations
from src.lineage.datasets import TRADING_INGESTION

default_args = {
    "owner": "data-eng",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="noaa_trading_observations",
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
    default_args=default_args,
    tags=["trading", "noaa"],
) as dag:

    ingest = PythonOperator(
        task_id="ingest_noaa_observations",
        python_callable=ingest_noaa_observations,
    )

    publish_dataset = EmptyOperator(
        task_id="publish_trading_ingestion",
        outlets=[TRADING_INGESTION],
    )

    ingest >> publish_dataset
