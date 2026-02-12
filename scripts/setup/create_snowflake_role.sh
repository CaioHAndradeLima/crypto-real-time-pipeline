#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

echo "Create Snowflake role and terraform user"

load_env
require_cmd snowsql

SNOWSQL_PWD="$SNOWFLAKE_PASSWORD"

echo "May you need inform you Snowflake Account password"
echo ""

snowsql \
  -a "$SNOWFLAKE_ACCOUNT-$SNOWFLAKE_ORGANIZATION_NAME" \
  -u "$SNOWFLAKE_USER" \
  -r "$SNOWFLAKE_ROLE" \
  -w "$SNOWFLAKE_WAREHOUSE" \
  -d "$SNOWFLAKE_DATABASE" \
  -f "$PROJECT_ROOT/infra/remote/snowflake/setup/roles.sql" \
  -s "$SNOWFLAKE_SCHEMA" \
  -o log_level=DEBUG

echo "Created/updated TERRAFORM_ROLE and TERRAFORM_USER from roles.sql"
