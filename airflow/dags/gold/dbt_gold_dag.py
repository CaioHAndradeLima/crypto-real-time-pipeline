from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.models import Variable
from airflow.operators.empty import EmptyOperator
from src.lineage.datasets import TRADING_SILVER, TRADING_GOLD

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
    dag_id="dbt_gold_layer",
    description="Run dbt Gold models in Snowflake",
    default_args=DEFAULT_ARGS,
    start_date=datetime(2024, 1, 1),
    schedule=[TRADING_SILVER],
    catchup=False,
    tags=["dbt", "gold", "snowflake"],
    is_paused_upon_creation=False,
) as dag:
    start = EmptyOperator(task_id="start")
    end = EmptyOperator(
        task_id="end",
        outlets=[TRADING_GOLD],
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
    # dbt run (gold)
    # ---------------------------------------------------
    dbt_run_gold = BashOperator(
        task_id="dbt_run_gold",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt run "
            f"--select gold "
            f"--target {DBT_TARGET} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
        inlets=[TRADING_SILVER],
    )

    # ---------------------------------------------------
    # dbt test (gold)
    # ---------------------------------------------------
    dbt_test_gold = BashOperator(
        task_id="dbt_test_gold",
        bash_command=(
            f"cd {DBT_PROJECT_DIR} && "
            f"dbt test "
            f"--select gold "
            f"--target {DBT_TARGET} "
            f"--profiles-dir {DBT_PROFILES_DIR}"
        ),
    )

    # ---------------------------------------------------
    # Task dependencies
    # ---------------------------------------------------
    start >> dbt_deps >> dbt_run_gold >> dbt_test_gold >> end
