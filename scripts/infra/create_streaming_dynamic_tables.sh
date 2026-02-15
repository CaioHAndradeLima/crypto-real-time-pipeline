#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file
require_cmd snowsql

# shellcheck source=/dev/null
source "$ENV_FILE"

required_vars=(
  SNOWFLAKE_ACCOUNT
  SNOWFLAKE_ORGANIZATION_NAME
  SNOWFLAKE_USER
  SNOWFLAKE_PASSWORD
  SNOWFLAKE_ROLE
  SNOWFLAKE_WAREHOUSE
  SNOWFLAKE_DATABASE
  SNOWFLAKE_SCHEMA
)

for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    echo "Missing env var: $var_name"
    exit 1
  fi
done

account_id="${SNOWFLAKE_ACCOUNT_IDENTIFIER:-${SNOWFLAKE_ORGANIZATION_NAME}-${SNOWFLAKE_ACCOUNT}}"
streaming_sql_dir="$PROJECT_ROOT/infra/remote/snowflake/setup/streaming"

if [ ! -d "$streaming_sql_dir" ]; then
  echo "Missing directory: $streaming_sql_dir"
  exit 1
fi

for sql_file in "$streaming_sql_dir"/*.sql; do
  echo "Applying: $(basename "$sql_file")"
  SNOWSQL_PWD="$SNOWFLAKE_PASSWORD" snowsql \
    -a "$account_id" \
    -u "$SNOWFLAKE_USER" \
    -r "$SNOWFLAKE_ROLE" \
    -w "$SNOWFLAKE_WAREHOUSE" \
    -d "$SNOWFLAKE_DATABASE" \
    -s "$SNOWFLAKE_SCHEMA" \
    -f "$sql_file" \
    -o exit_on_error=true \
    -o log_level=ERROR
done

echo "Dynamic tables created/updated:"
echo "- TRADING_ANALYTICS.SILVER.TRADES_CLEAN_DT"
echo "- TRADING_ANALYTICS.GOLD.TRADES_1M_DT"
