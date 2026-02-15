from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from streaming_ops.airflow_callbacks import slack_task_failure_callback
from streaming_ops.governance_service import StreamingGovernanceService

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
    "on_failure_callback": slack_task_failure_callback,
}

governance_service = StreamingGovernanceService()

with DAG(
    dag_id="streaming_cost_governance",
    description="Apply warehouse guardrails and monitor credit threshold",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule="0 * * * *",
    catchup=False,
    tags=["streaming", "governance", "cost"],
    is_paused_upon_creation=False,
) as dag:
    enforce_policies = PythonOperator(
        task_id="enforce_warehouse_policies",
        python_callable=governance_service.enforce_warehouse_policies,
    )

    credit_guardrail = PythonOperator(
        task_id="emit_credit_guardrail",
        python_callable=governance_service.emit_credit_guardrail,
    )

    enforce_policies >> credit_guardrail
