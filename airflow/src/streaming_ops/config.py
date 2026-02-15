from dataclasses import dataclass
import os


@dataclass(frozen=True)
class StreamingConfig:
    connect_url: str
    connector_name: str
    kafka_topic_trades: str
    snowflake_account: str
    snowflake_organization_name: str
    snowflake_account_identifier: str
    snowflake_url_name: str
    snowflake_user: str
    snowflake_private_key: str
    snowflake_private_key_passphrase: str
    snowflake_password: str
    snowflake_database: str
    snowflake_schema: str
    snowflake_role: str
    snowflake_warehouse: str
    snowflake_trades_raw_table: str

    @classmethod
    def from_env(cls) -> "StreamingConfig":
        account = os.environ["SNOWFLAKE_ACCOUNT"]
        organization = os.environ["SNOWFLAKE_ORGANIZATION_NAME"]
        account_identifier = os.getenv(
            "SNOWFLAKE_ACCOUNT_IDENTIFIER", f"{organization}-{account}"
        )

        return cls(
            connect_url=os.getenv("CONNECT_URL", "http://host.docker.internal:8083"),
            connector_name=os.getenv("CONNECTOR_NAME", "snowflake-trades-sink"),
            kafka_topic_trades=os.getenv("KAFKA_TOPIC_TRADES", "crypto_trades"),
            snowflake_account=account,
            snowflake_organization_name=organization,
            snowflake_account_identifier=account_identifier,
            snowflake_url_name=os.getenv(
                "SNOWFLAKE_URL_NAME",
                f"{account_identifier}.snowflakecomputing.com",
            ),
            snowflake_user=os.environ["SNOWFLAKE_USER"],
            snowflake_private_key=os.environ["SNOWFLAKE_PRIVATE_KEY"],
            snowflake_private_key_passphrase=os.getenv(
                "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE", ""
            ),
            snowflake_password=os.environ["SNOWFLAKE_PASSWORD"],
            snowflake_database=os.getenv("SNOWFLAKE_DATABASE", "TRADING_ANALYTICS"),
            snowflake_schema="BRONZE",
            snowflake_role=os.environ["SNOWFLAKE_ROLE"],
            snowflake_warehouse=os.getenv("SNOWFLAKE_WAREHOUSE", "TRADING_WH"),
            snowflake_trades_raw_table="TRADES_RAW",
        )
