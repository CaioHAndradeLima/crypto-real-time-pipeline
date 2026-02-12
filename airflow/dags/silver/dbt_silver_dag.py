from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from src.lineage.datasets import TRADING_BRONZE, TRADING_SILVER

# -------------------------------------------------------
# Config
# -------------------------------------------------------
DBT_PROJECT_DIR = "/opt/airflow/dbt"
DBT_PROFILES_DIR = "/opt/airflow/dbt"
DBT_TARGET = Variable.get("dbt_target", default_var="dev")

DEFAULT_ARGS = {
    "owner": "data-engineering",
    "depends_on_past": False,
    "retries": 0,
    "retry_delay": timedelta(minutes=1),
}

# -------------------------------------------------------
# DAG
# -------------------------------------------------------
with DAG(
    dag_id="dbt_silver_layer",
    description="Run dbt Silver models in Snowflake",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=[TRADING_BRONZE],
    catchup=False,
    tags=["dbt", "silver", "snowflake"],
    is_paused_upon_creation=False,
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(
        task_id="Trigger_DBT_Gold",
        outlets=[TRADING_SILVER],
    )

    # ---------------------------------------------------
    # dbt deps
    # ---------------------------------------------------
    dbt_deps = BashOperator(
        task_id="dbt_deps",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt deps "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    # ---------------------------------------------------
    # dbt run (silver)
    # ---------------------------------------------------
    dbt_run_silver = BashOperator(
        task_id="dbt_run_silver",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run "
            f"--select silver "
            f"--target {DBT_TARGET} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    # ---------------------------------------------------
    # dbt test (silver)
    # ---------------------------------------------------
    dbt_test_silver = BashOperator(
        task_id="dbt_test_silver",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt test "
            f"--select silver "
            f"--target {DBT_TARGET} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    # ---------------------------------------------------
    # Task dependencies
    # ---------------------------------------------------
    start >> dbt_deps >> dbt_run_silver >> dbt_test_silver >> end
