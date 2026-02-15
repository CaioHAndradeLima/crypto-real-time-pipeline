from .config import StreamingConfig
from .connector_client import KafkaConnectClient
from .snowflake_client import SnowflakeClient


class StreamingHealthcheckService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.connector_client = KafkaConnectClient(self.config)
        self.snowflake_client = SnowflakeClient(self.config)

    def check_connector(self) -> None:
        self.connector_client.assert_connector_running()

    def check_data_freshness(self) -> None:
        self.snowflake_client.assert_recent_bronze_rows(window_minutes=5)
        self.snowflake_client.assert_silver_lag(max_lag_seconds=600)
