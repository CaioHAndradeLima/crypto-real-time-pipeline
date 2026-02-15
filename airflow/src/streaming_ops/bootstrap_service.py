from .config import StreamingConfig
from .connector_client import KafkaConnectClient
from .snowflake_client import SnowflakeClient
from .sql_definitions import STREAMING_DYNAMIC_TABLE_STATEMENTS


class StreamingBootstrapService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.connector_client = KafkaConnectClient(self.config)
        self.snowflake_client = SnowflakeClient(self.config)

    def configure_connector(self) -> None:
        self.connector_client.upsert_snowflake_sink_connector()

    def apply_dynamic_tables(self) -> None:
        self.snowflake_client.execute_statements(STREAMING_DYNAMIC_TABLE_STATEMENTS)
