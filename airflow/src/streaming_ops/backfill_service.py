from .bootstrap_service import StreamingBootstrapService
from .config import StreamingConfig


class StreamingBackfillService:
    def __init__(self, config: StreamingConfig | None = None) -> None:
        self.config = config or StreamingConfig.from_env()
        self.bootstrap_service = StreamingBootstrapService(self.config)

    def rebuild_dynamic_tables(self) -> None:
        # For dynamic-table based pipelines, "backfill" is typically done by
        # re-applying definitions and letting Snowflake recompute from bronze history.
        self.bootstrap_service.apply_dynamic_tables()
