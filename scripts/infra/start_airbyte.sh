#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file

echo "[2/4] Start Airbyte"
chmod +x "$AIRBYTE_DIR"/*.sh
(
  cd "$AIRBYTE_DIR"
  bash ./start_airbyte.sh
)
