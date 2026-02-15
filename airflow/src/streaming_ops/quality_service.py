from .config import StreamingConfig
from .snowflake_client import SnowflakeClient


class StreamingQualityService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.snowflake_client = SnowflakeClient(self.config)

    def check_silver_no_duplicates(self) -> None:
        row = self.snowflake_client.fetch_one(
            """
            select count(*)
            from (
              select symbol, trade_id, count(*) as c
              from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
              group by symbol, trade_id
              having count(*) > 1
            )
            """
        )
        duplicate_keys = row[0] if row else 0
        if duplicate_keys > 0:
            raise RuntimeError(f"Silver has duplicate key groups: {duplicate_keys}")

    def check_silver_not_nulls(self) -> None:
        row = self.snowflake_client.fetch_one(
            """
            select count(*)
            from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
            where symbol is null
               or trade_id is null
               or trade_time is null
               or price is null
               or quantity is null
            """
        )
        null_rows = row[0] if row else 0
        if null_rows > 0:
            raise RuntimeError(f"Silver contains invalid null rows: {null_rows}")

    def check_recent_activity(self, min_rows_last_5m: int = 10) -> None:
        row = self.snowflake_client.fetch_one(
            """
            select count(*)
            from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
            where trade_time >= dateadd('minute', -5, current_timestamp())
            """
        )
        recent_rows = row[0] if row else 0
        if recent_rows < min_rows_last_5m:
            raise RuntimeError(
                f"Low recent activity in silver: {recent_rows} rows (threshold {min_rows_last_5m})"
            )
