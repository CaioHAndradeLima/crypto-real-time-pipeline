import json
from urllib.request import Request, urlopen

from .config import StreamingConfig


class KafkaConnectClient:
    def __init__(self, config: StreamingConfig) -> None:
        self.config = config

    def upsert_snowflake_sink_connector(self) -> None:
        payload = {
            "connector.class": "com.snowflake.kafka.connector.SnowflakeSinkConnector",
            "tasks.max": "1",
            "topics": self.config.kafka_topic_trades,
            "snowflake.url.name": self.config.snowflake_url_name,
            "snowflake.user.name": self.config.snowflake_user,
            "snowflake.private.key": self.config.snowflake_private_key,
            "snowflake.private.key.passphrase": self.config.snowflake_private_key_passphrase,
            "snowflake.database.name": self.config.snowflake_database,
            "snowflake.schema.name": self.config.snowflake_schema,
            "snowflake.role.name": self.config.snowflake_role,
            "snowflake.warehouse.name": self.config.snowflake_warehouse,
            "snowflake.ingestion.method": "SNOWPIPE_STREAMING",
            "buffer.count.records": "1000",
            "buffer.flush.time": "10",
            "buffer.size.bytes": "5000000",
            "key.converter": "org.apache.kafka.connect.storage.StringConverter",
            "value.converter": "org.apache.kafka.connect.json.JsonConverter",
            "value.converter.schemas.enable": "false",
            "snowflake.topic2table.map": (
                f"{self.config.kafka_topic_trades}:{self.config.snowflake_trades_raw_table}"
            ),
            "errors.tolerance": "all",
            "errors.log.enable": "true",
        }

        req = Request(
            f"{self.config.connect_url}/connectors/{self.config.connector_name}/config",
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="PUT",
        )
        with urlopen(req, timeout=30) as response:
            if response.status // 100 != 2:
                raise RuntimeError(f"Connector configure failed with status {response.status}")

    def assert_connector_running(self) -> None:
        payload = self.get_status()
        connector_state = payload.get("connector", {}).get("state")
        if connector_state != "RUNNING":
            raise RuntimeError(f"Connector state is {connector_state}, expected RUNNING")

        tasks = payload.get("tasks", [])
        if not tasks:
            raise RuntimeError("Connector has no running tasks")

        for task in tasks:
            if task.get("state") != "RUNNING":
                raise RuntimeError(f"Connector task not running: {task}")

    def get_status(self) -> dict:
        status_url = f"{self.config.connect_url}/connectors/{self.config.connector_name}/status"
        with urlopen(status_url, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))

    def delete_connector(self) -> None:
        req = Request(
            f"{self.config.connect_url}/connectors/{self.config.connector_name}",
            method="DELETE",
        )
        with urlopen(req, timeout=15) as response:
            if response.status not in (200, 202, 204):
                raise RuntimeError(f"Connector delete failed with status {response.status}")
