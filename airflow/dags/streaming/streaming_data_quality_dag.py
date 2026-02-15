from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from streaming_ops.airflow_callbacks import slack_task_failure_callback
from streaming_ops.quality_service import StreamingQualityService

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
    "on_failure_callback": slack_task_failure_callback,
}

quality_service = StreamingQualityService()

with DAG(
    dag_id="streaming_data_quality",
    description="Data quality checks for silver streaming layer",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule="*/15 * * * *",
    catchup=False,
    tags=["streaming", "quality", "ops"],
    is_paused_upon_creation=False,
) as dag:
    null_check = PythonOperator(
        task_id="check_silver_not_nulls",
        python_callable=quality_service.check_silver_not_nulls,
    )

    duplicate_check = PythonOperator(
        task_id="check_silver_no_duplicates",
        python_callable=quality_service.check_silver_no_duplicates,
    )

    activity_check = PythonOperator(
        task_id="check_recent_activity",
        python_callable=quality_service.check_recent_activity,
    )

    null_check >> duplicate_check >> activity_check
