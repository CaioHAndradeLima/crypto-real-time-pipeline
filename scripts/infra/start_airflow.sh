#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file

echo "[4/4] Start Airflow"
docker compose \
  --env-file "$ENV_FILE" \
  -f "$AIRFLOW_COMPOSE_FILE" \
  up -d

echo "Airflow user: admin password: admin"
