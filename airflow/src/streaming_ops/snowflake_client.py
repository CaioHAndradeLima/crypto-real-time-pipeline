import snowflake.connector

from .config import StreamingConfig


class SnowflakeClient:
    def __init__(self, config: StreamingConfig) -> None:
        self.config = config

    def _connect(self):
        return snowflake.connector.connect(
            account=self.config.snowflake_account_identifier,
            user=self.config.snowflake_user,
            password=self.config.snowflake_password,
            role=self.config.snowflake_role,
            warehouse=self.config.snowflake_warehouse,
            database=self.config.snowflake_database,
            schema=self.config.snowflake_schema,
        )

    def execute_statements(self, statements: list[str]) -> None:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                for statement in statements:
                    cur.execute(statement)
        finally:
            conn.close()

    def assert_recent_bronze_rows(self, window_minutes: int = 5) -> None:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    f"""
                    select count(*) as recent_rows
                    from TRADING_ANALYTICS.BRONZE.TRADES_RAW
                    where to_timestamp_ntz(record_content:T::number, 3) >= dateadd('minute', -{window_minutes}, current_timestamp())
                    """
                )
                recent_rows = cur.fetchone()[0]
                if recent_rows is None or recent_rows <= 0:
                    raise RuntimeError(
                        f"No recent rows in BRONZE.TRADES_RAW for last {window_minutes} minutes"
                    )
        finally:
            conn.close()

    def assert_silver_lag(self, max_lag_seconds: int = 600) -> None:
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    select datediff(
                      'second',
                      max(ingested_at),
                      current_timestamp()
                    ) as lag_seconds
                    from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
                    """
                )
                lag_seconds = cur.fetchone()[0]
                if lag_seconds is None or lag_seconds > max_lag_seconds:
                    raise RuntimeError(f"Silver lag too high: {lag_seconds} seconds")
        finally:
            conn.close()
