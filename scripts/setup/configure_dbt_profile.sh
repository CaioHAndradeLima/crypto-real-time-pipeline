#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

echo "Configure dbt/profiles.yml"

load_env

DBT_DIR="$PROJECT_ROOT/dbt"
DBT_PROFILES_FILE="$DBT_DIR/profiles.yml"
mkdir -p "$DBT_DIR"

cat >"$DBT_PROFILES_FILE" <<EOF
weather_pipeline:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: $SNOWFLAKE_ACCOUNT
      user: $SNOWFLAKE_USER
      password: $SNOWFLAKE_PASSWORD
      role: $SNOWFLAKE_ROLE
      warehouse: $SNOWFLAKE_WAREHOUSE
      database: $SNOWFLAKE_DATABASE
      schema: $SNOWFLAKE_SCHEMA
      threads: 4
EOF

echo "dbt profile created at $DBT_PROFILES_FILE"
