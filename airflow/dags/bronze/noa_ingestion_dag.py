from airflow.datasets import Dataset
from airflow import DAG
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

from src.ingestion.noaa.noaa_observations_ingest import ingest_noaa_observations
from src.lineage.datasets import WEATHER_INGESTION

default_args = {
    "owner": "data-eng",
    "retries": 3,
    "retry_delay": timedelta(minutes=5),
}

with DAG(
    dag_id="noaa_weather_observations",
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
    default_args=default_args,
    tags=["weather", "noaa"],
) as dag:

    ingest = PythonOperator(
        task_id="ingest_noaa_observations",
        python_callable=ingest_noaa_observations,
    )

    publish_dataset = EmptyOperator(
        task_id="publish_weather_ingestion",
        outlets=[WEATHER_INGESTION],
    )

    ingest >> publish_dataset
