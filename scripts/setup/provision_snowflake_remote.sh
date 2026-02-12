#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/common.sh"

echo "Provision Snowflake remote infrastructure with Terraform"

load_env
require_cmd terraform

export TF_VAR_snowflake_account_name="$SNOWFLAKE_ACCOUNT"
export TF_VAR_snowflake_organization_name="${SNOWFLAKE_ORGANIZATION_NAME}"
export TF_VAR_snowflake_user="$SNOWFLAKE_USER"
export TF_VAR_snowflake_password="$SNOWFLAKE_PASSWORD"
export TF_VAR_snowflake_role="$SNOWFLAKE_ROLE"

pushd "$PROJECT_ROOT/infra/remote/snowflake" >/dev/null

terraform init

if ! terraform state show snowflake_warehouse.weather_wh >/dev/null 2>&1; then
  echo "Importing existing Snowflake resources into Terraform state"
  terraform import snowflake_warehouse.weather_wh WEATHER_WH
  terraform import snowflake_database.weather_analytics WEATHER_ANALYTICS
  terraform import snowflake_schema.bronze "WEATHER_ANALYTICS.BRONZE"
  terraform import snowflake_schema.silver "WEATHER_ANALYTICS.SILVER"
  terraform import snowflake_schema.gold "WEATHER_ANALYTICS.GOLD"
else
  echo "Warehouse WEATHER_WH already managed by Terraform"
fi

terraform plan
terraform apply -auto-approve

popd >/dev/null

echo "Snowflake remote infrastructure created."
