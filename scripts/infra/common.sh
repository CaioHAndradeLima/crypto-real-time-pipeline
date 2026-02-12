#!/bin/bash
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
ENV_FILE="$PROJECT_ROOT/.env"
LOCAL_INFRA_DIR="$PROJECT_ROOT/infra/local"
AIRBYTE_DIR="$LOCAL_INFRA_DIR/airbyte"
POSTGRES_COMPOSE_FILE="$LOCAL_INFRA_DIR/postgres/docker-compose.yml"
AIRFLOW_COMPOSE_FILE="$LOCAL_INFRA_DIR/airflow/docker-compose.yml"

require_env_file() {
  if [ ! -f "$ENV_FILE" ]; then
    echo "Missing $ENV_FILE. Run 'make create-env' first."
    exit 1
  fi
}
