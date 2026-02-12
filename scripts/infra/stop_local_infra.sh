#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

echo "Stop local infra"
abctl local uninstall || true
rm -rf ~/.airbyte/abctl/data

docker compose -f "$POSTGRES_COMPOSE_FILE" down -v
docker compose -f "$AIRFLOW_COMPOSE_FILE" down -v
