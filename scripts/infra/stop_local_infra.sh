#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

echo "Stop local infra"

docker compose -f "$AIRFLOW_COMPOSE_FILE" down -v
docker compose -f "$KAFKA_CONNECT_COMPOSE_FILE" down -v
