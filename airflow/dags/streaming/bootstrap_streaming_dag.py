from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator

from streaming_ops.bootstrap_service import StreamingBootstrapService

DEFAULT_ARGS = {"owner": "data-engineering", "depends_on_past": False, "retries": 0}
bootstrap_service = StreamingBootstrapService()


with DAG(
    dag_id="bootstrap_streaming_stack",
    description="Initialize connector and dynamic tables",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["streaming", "ops", "bootstrap"],
    is_paused_upon_creation=False,
) as dag:
    configure_sink = PythonOperator(
        task_id="configure_snowflake_kafka_sink",
        python_callable=bootstrap_service.configure_connector,
    )

    apply_dynamic_table_defs = PythonOperator(
        task_id="apply_dynamic_table_definitions",
        python_callable=bootstrap_service.apply_dynamic_tables,
    )

    configure_sink >> apply_dynamic_table_defs
