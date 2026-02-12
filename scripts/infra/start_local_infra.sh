#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Start local infra: postgres -> airbyte -> configure airbyte -> airflow"
bash "$SCRIPT_DIR/start_postgres.sh"
bash "$SCRIPT_DIR/start_airbyte.sh"
bash "$SCRIPT_DIR/configure_airbyte.sh"
bash "$SCRIPT_DIR/start_airflow.sh"
