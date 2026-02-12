#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file

echo "Start Kafka + Kafka Connect"
docker compose \
  --env-file "$ENV_FILE" \
  -f "$KAFKA_CONNECT_COMPOSE_FILE" \
  up -d
