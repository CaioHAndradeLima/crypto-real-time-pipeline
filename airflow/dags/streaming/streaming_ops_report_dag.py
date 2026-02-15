from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from streaming_ops.airflow_callbacks import slack_task_failure_callback
from streaming_ops.reporting_service import StreamingReportingService

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
    "on_failure_callback": slack_task_failure_callback,
}

reporting_service = StreamingReportingService()

with DAG(
    dag_id="streaming_ops_report",
    description="Daily operational summary for streaming pipeline",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule="0 9 * * *",
    catchup=False,
    tags=["streaming", "reporting", "ops"],
    is_paused_upon_creation=False,
) as dag:
    send_report = PythonOperator(
        task_id="send_daily_streaming_summary",
        python_callable=reporting_service.send_daily_summary,
    )

    send_report
