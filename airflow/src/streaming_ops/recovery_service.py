from urllib.error import HTTPError

from .bootstrap_service import StreamingBootstrapService
from .config import StreamingConfig
from .connector_client import KafkaConnectClient
from .healthcheck_service import StreamingHealthcheckService


class StreamingRecoveryService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.connector_client = KafkaConnectClient(self.config)
        self.bootstrap_service = StreamingBootstrapService(self.config)
        self.healthcheck_service = StreamingHealthcheckService(self.config)

    def recover_connector(self) -> None:
        try:
            self.connector_client.delete_connector()
        except HTTPError as exc:
            if exc.code != 404:
                raise
        self.bootstrap_service.configure_connector()

    def validate_recovery(self) -> None:
        self.healthcheck_service.check_connector()
        self.healthcheck_service.check_data_freshness()
