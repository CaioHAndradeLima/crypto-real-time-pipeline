from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from streaming_ops.airflow_callbacks import slack_task_failure_callback
from streaming_ops.recovery_service import StreamingRecoveryService

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
    "on_failure_callback": slack_task_failure_callback,
}

recovery_service = StreamingRecoveryService()

with DAG(
    dag_id="streaming_recovery",
    description="Manual recovery workflow for connector and freshness",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["streaming", "recovery", "ops"],
    is_paused_upon_creation=False,
) as dag:
    recover_connector = PythonOperator(
        task_id="recover_connector",
        python_callable=recovery_service.recover_connector,
    )

    validate = PythonOperator(
        task_id="validate_recovery",
        python_callable=recovery_service.validate_recovery,
    )

    recover_connector >> validate
