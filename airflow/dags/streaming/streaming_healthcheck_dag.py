from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from streaming_ops.healthcheck_service import StreamingHealthcheckService

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}
healthcheck_service = StreamingHealthcheckService()


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
        python_callable=healthcheck_service.check_connector,
    )

    freshness = PythonOperator(
        task_id="check_streaming_freshness",
        python_callable=healthcheck_service.check_data_freshness,
    )

    connector_health >> freshness
