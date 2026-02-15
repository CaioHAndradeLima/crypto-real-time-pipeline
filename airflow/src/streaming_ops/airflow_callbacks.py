from airflow.utils.context import Context

from .alerting import SlackNotifier


def slack_task_failure_callback(context: Context) -> None:
    dag_id = context.get("dag").dag_id if context.get("dag") else "unknown_dag"
    task_id = context.get("task_instance").task_id if context.get("task_instance") else "unknown_task"
    run_id = context.get("run_id", "unknown_run")
    exception = context.get("exception")
    log_url = context.get("task_instance").log_url if context.get("task_instance") else ""

    message = (
        f":red_circle: Airflow task failure\n"
        f"DAG: `{dag_id}`\n"
        f"Task: `{task_id}`\n"
        f"Run: `{run_id}`\n"
        f"Error: `{exception}`\n"
        f"Logs: {log_url}"
    )

    SlackNotifier().send(message)
