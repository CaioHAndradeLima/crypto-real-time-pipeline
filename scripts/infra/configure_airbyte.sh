#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file

echo "[3/4] Configure Airbyte"
chmod +x "$AIRBYTE_DIR"/*.sh
(
  cd "$AIRBYTE_DIR"
  bash ./setup_credentials.sh
  bash ./setup_postgres_source.sh
  bash ./setup_snowflake_destination.sh
  bash ./generate_ingestion_json.sh
  bash ./create_connections.sh
)
