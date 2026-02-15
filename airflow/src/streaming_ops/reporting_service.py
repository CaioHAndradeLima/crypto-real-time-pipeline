from .alerting import SlackNotifier
from .config import StreamingConfig
from .snowflake_client import SnowflakeClient


class StreamingReportingService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.snowflake_client = SnowflakeClient(self.config)
        self.notifier = SlackNotifier()

    def send_daily_summary(self) -> None:
        bronze_row = self.snowflake_client.fetch_one(
            """
            select count(*)
            from TRADING_ANALYTICS.BRONZE.TRADES_RAW
            where to_timestamp_ntz(record_content:T::number, 3) >= dateadd('day', -1, current_timestamp())
            """
        )
        silver_row = self.snowflake_client.fetch_one(
            """
            select count(*)
            from TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT
            where trade_time >= dateadd('day', -1, current_timestamp())
            """
        )
        gold_row = self.snowflake_client.fetch_one(
            """
            select count(*)
            from TRADING_ANALYTICS.GOLD.TRADES_1M_DT
            where minute_bucket >= dateadd('day', -1, current_timestamp())
            """
        )

        bronze_count = bronze_row[0] if bronze_row else 0
        silver_count = silver_row[0] if silver_row else 0
        gold_count = gold_row[0] if gold_row else 0

        message = (
            ":bar_chart: Streaming Daily Summary\n"
            f"- Bronze rows (24h): {bronze_count}\n"
            f"- Silver rows (24h): {silver_count}\n"
            f"- Gold 1m buckets (24h): {gold_count}"
        )
        self.notifier.send(message)
