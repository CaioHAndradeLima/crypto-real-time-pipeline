#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Start local infra: airflow"
bash "$SCRIPT_DIR/start_airflow.sh"
