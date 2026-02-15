from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from streaming_ops.airflow_callbacks import slack_task_failure_callback
from streaming_ops.backfill_service import StreamingBackfillService

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
    "on_failure_callback": slack_task_failure_callback,
}

backfill_service = StreamingBackfillService()

with DAG(
    dag_id="streaming_backfill",
    description="Manual dynamic-table rebuild from bronze history",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["streaming", "backfill", "ops"],
    is_paused_upon_creation=False,
) as dag:
    rebuild = PythonOperator(
        task_id="rebuild_dynamic_tables",
        python_callable=backfill_service.rebuild_dynamic_tables,
    )

    rebuild
