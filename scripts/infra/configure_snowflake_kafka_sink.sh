#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file
source "$ENV_FILE"

CONNECT_URL="${CONNECT_URL:-http://localhost:8083}"
CONNECTOR_NAME="${CONNECTOR_NAME:-snowflake-trades-sink}"
TOPIC_NAME="${KAFKA_TOPIC_TRADES:-crypto_trades}"
WAREHOUSE_NAME="${SNOWFLAKE_WAREHOUSE:-TRADING_WH}"
TABLE_NAME="TRADES_RAW"
SCHEMA_NAME="BRONZE"
SCHEMA_NAME_UPPER="$(printf '%s' "$SCHEMA_NAME" | tr '[:lower:]' '[:upper:]')"
TABLE_NAME_UPPER="$(printf '%s' "$TABLE_NAME" | tr '[:lower:]' '[:upper:]')"

required_vars=(
  SNOWFLAKE_ACCOUNT
  SNOWFLAKE_ORGANIZATION_NAME
  SNOWFLAKE_USER
  SNOWFLAKE_PRIVATE_KEY
  SNOWFLAKE_DATABASE
  SNOWFLAKE_ROLE
)

for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    echo "Missing env var: $var_name"
    exit 1
  fi
done

SNOWFLAKE_ACCOUNT_IDENTIFIER="${SNOWFLAKE_ACCOUNT_IDENTIFIER:-${SNOWFLAKE_ORGANIZATION_NAME}-${SNOWFLAKE_ACCOUNT}}"
SNOWFLAKE_URL_NAME="${SNOWFLAKE_URL_NAME:-${SNOWFLAKE_ACCOUNT_IDENTIFIER}.snowflakecomputing.com}"

if [ "$SCHEMA_NAME_UPPER" != "BRONZE" ]; then
  echo "This connector is restricted to BRONZE raw ingestion. Set SNOWFLAKE_SCHEMA=BRONZE."
  exit 1
fi

if [ "$TABLE_NAME_UPPER" != "TRADES_RAW" ]; then
  echo "This connector is restricted to BRONZE.TRADES_RAW. Set SNOWFLAKE_TRADES_RAW_TABLE=TRADES_RAW."
  exit 1
fi

if [ -n "${SNOWFLAKE_PASSWORD:-}" ]; then
  echo "Warning: SNOWFLAKE_PASSWORD is ignored by Snowflake Kafka Connector 3.5.3."
  echo "Using key-pair auth with SNOWFLAKE_PRIVATE_KEY."
fi

echo "Waiting for Kafka Connect at $CONNECT_URL"
is_up=0
for _ in $(seq 1 60); do
  if curl -fsS "$CONNECT_URL/connectors" >/dev/null; then
    is_up=1
    break
  fi
  sleep 2
done

if [ "$is_up" -ne 1 ]; then
  echo "Kafka Connect is not reachable at $CONNECT_URL"
  exit 1
fi

echo "Validating Snowflake connector plugin availability"
if ! curl -fsS "$CONNECT_URL/connector-plugins" | grep -q "com.snowflake.kafka.connector.SnowflakeSinkConnector"; then
  echo "Snowflake sink plugin is not available in Kafka Connect."
  echo "Check container logs: docker logs local-kafka-connect"
  exit 1
fi

echo "Register or update connector: $CONNECTOR_NAME"
tmp_body="$(mktemp)"
http_code="$(
  curl -sS -o "$tmp_body" -w "%{http_code}" -X PUT "$CONNECT_URL/connectors/$CONNECTOR_NAME/config" \
  -H "Content-Type: application/json" \
  -d "{
    \"connector.class\": \"com.snowflake.kafka.connector.SnowflakeSinkConnector\",
    \"tasks.max\": \"1\",
    \"topics\": \"$TOPIC_NAME\",
    \"snowflake.url.name\": \"$SNOWFLAKE_URL_NAME\",
    \"snowflake.user.name\": \"$SNOWFLAKE_USER\",
    \"snowflake.private.key\": \"$SNOWFLAKE_PRIVATE_KEY\",
    \"snowflake.private.key.passphrase\": \"${SNOWFLAKE_PRIVATE_KEY_PASSPHRASE:-}\",
    \"snowflake.database.name\": \"$SNOWFLAKE_DATABASE\",
    \"snowflake.schema.name\": \"$SCHEMA_NAME\",
    \"snowflake.role.name\": \"$SNOWFLAKE_ROLE\",
    \"snowflake.warehouse.name\": \"$WAREHOUSE_NAME\",
    \"snowflake.ingestion.method\": \"SNOWPIPE_STREAMING\",
    \"buffer.count.records\": \"1000\",
    \"buffer.flush.time\": \"10\",
    \"buffer.size.bytes\": \"5000000\",
    \"key.converter\": \"org.apache.kafka.connect.storage.StringConverter\",
    \"value.converter\": \"org.apache.kafka.connect.json.JsonConverter\",
    \"value.converter.schemas.enable\": \"false\",
    \"snowflake.topic2table.map\": \"$TOPIC_NAME:$TABLE_NAME\",
    \"errors.tolerance\": \"all\",
    \"errors.log.enable\": \"true\"
  }"
)"

if [ "${http_code#2}" = "$http_code" ]; then
  echo "Kafka Connect returned HTTP $http_code while creating connector:"
  cat "$tmp_body"
  rm -f "$tmp_body"
  exit 1
fi

rm -f "$tmp_body"

echo ""
echo "Connector configured. Check status:"
echo "curl -s $CONNECT_URL/connectors/$CONNECTOR_NAME/status"
