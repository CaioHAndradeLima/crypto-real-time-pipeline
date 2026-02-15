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

    def fetch_one(self, query: str):
        conn = self._connect()
        try:
            with conn.cursor() as cur:
                cur.execute(query)
                return cur.fetchone()
        finally:
            conn.close()

    def assert_recent_bronze_rows(self, window_minutes: int = 5) -> None:
        minutes = max(int(window_minutes), 1)
        query = f"""
            select
              count(*) as recent_rows,
              max(to_timestamp_ntz(record_content:T::number, 3)) as max_event_ts_utc
            from TRADING_ANALYTICS.BRONZE.TRADES_RAW
            where to_timestamp_ntz(record_content:T::number, 3) >=
                  dateadd(minute, -{minutes}, convert_timezone('UTC', current_timestamp())::timestamp_ntz)
        """
        row = self.fetch_one(query)
        recent_rows = row[0] if row else None
        if recent_rows is None or recent_rows <= 0:
            raise RuntimeError(
                f"No recent rows in BRONZE.TRADES_RAW for last {minutes} minutes"
            )

    def assert_silver_lag(self, max_lag_seconds: int = 600) -> None:
        row = self.fetch_one("""
            select datediff(
              second,
              max(ingested_at),
              convert_timezone('UTC', current_timestamp())::timestamp_ntz
            ) as lag_seconds
            from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
            """)
        lag_seconds = row[0] if row else None
        if lag_seconds is None or lag_seconds > max_lag_seconds:
            raise RuntimeError(f"Silver lag too high: {lag_seconds} seconds")
