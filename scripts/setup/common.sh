#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="${ENV_FILE:-$PROJECT_ROOT/.env}"

SNOWFLAKE_WAREHOUSE="${SNOWFLAKE_WAREHOUSE:-WEATHER_WH}"
SNOWFLAKE_DATABASE="${SNOWFLAKE_DATABASE:-WEATHER_ANALYTICS}"
SNOWFLAKE_ROLE="${SNOWFLAKE_ROLE:-ACCOUNTADMIN}"
SNOWFLAKE_SCHEMA="${SNOWFLAKE_SCHEMA:-BRONZE}"

load_env() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Missing $ENV_FILE. Run scripts/setup/01_create_env.sh first."
    exit 1
  fi

  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
}

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1"
    exit 1
  fi
}
