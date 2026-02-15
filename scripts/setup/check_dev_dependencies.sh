#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

AUTO_INSTALL_SNOWSQL="${AUTO_INSTALL_SNOWSQL:-true}"
missing=0

check_cmd() {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[ok] $label"
  else
    echo "[missing] $label ($cmd)"
    missing=1
  fi
}

echo "Checking developer dependencies"

check_cmd python3 "Python 3"
check_cmd docker "Docker CLI"
check_cmd terraform "Terraform"
check_cmd make "GNU Make"

if command -v docker >/dev/null 2>&1; then
  if docker info >/dev/null 2>&1; then
    echo "[ok] Docker daemon"
  else
    echo "[missing] Docker daemon (start Docker Desktop/Engine)"
    missing=1
  fi
fi

if command -v snowsql >/dev/null 2>&1; then
  echo "[ok] SnowSQL CLI"
else
  echo "[missing] SnowSQL CLI"
  if [ "$AUTO_INSTALL_SNOWSQL" = "true" ]; then
    echo "Installing SnowSQL via brew cask"
    bash "$SCRIPT_DIR/install_snowflake_snowsql.sh"
    if command -v snowsql >/dev/null 2>&1; then
      echo "[ok] SnowSQL CLI installed"
    else
      echo "[missing] SnowSQL CLI install failed"
      missing=1
    fi
  else
    missing=1
  fi
fi

if [ "$missing" -ne 0 ]; then
  echo "One or more dependencies are missing."
  exit 1
fi

echo "All required developer dependencies are available."
