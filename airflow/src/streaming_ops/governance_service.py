from .config import StreamingConfig
from .snowflake_client import SnowflakeClient


class StreamingGovernanceService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.snowflake_client = SnowflakeClient(self.config)

    def enforce_warehouse_policies(self) -> None:
        warehouse = self.config.snowflake_warehouse
        self.snowflake_client.execute_statements(
            [
                f"ALTER WAREHOUSE IF EXISTS {warehouse} SET AUTO_SUSPEND = 60",
                f"ALTER WAREHOUSE IF EXISTS {warehouse} SET AUTO_RESUME = TRUE",
            ]
        )

    def emit_credit_guardrail(self, max_daily_credits: float = 100.0) -> None:
        row = self.snowflake_client.fetch_one(
            """
            select coalesce(sum(credits_used), 0)
            from snowflake.account_usage.warehouse_metering_history
            where warehouse_name = 'TRADING_WH'
              and start_time >= date_trunc('day', current_timestamp())
            """
        )
        credits = float(row[0]) if row and row[0] is not None else 0.0
        if credits > max_daily_credits:
            raise RuntimeError(
                f"Daily warehouse credits exceeded threshold: {credits} > {max_daily_credits}"
            )
