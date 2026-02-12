#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# shellcheck source=./common.sh
source "$SCRIPT_DIR/common.sh"

require_env_file
require_cmd openssl
require_cmd snowsql

# shellcheck source=/dev/null
source "$ENV_FILE"

required_vars=(
  SNOWFLAKE_ACCOUNT
  SNOWFLAKE_ORGANIZATION_NAME
  SNOWFLAKE_USER
  SNOWFLAKE_PASSWORD
  SNOWFLAKE_ROLE
  SNOWFLAKE_WAREHOUSE
  SNOWFLAKE_DATABASE
  SNOWFLAKE_SCHEMA
)

for var_name in "${required_vars[@]}"; do
  if [ -z "${!var_name:-}" ]; then
    echo "Missing env var: $var_name"
    exit 1
  fi
done

upsert_env() {
  local key="$1"
  local value="$2"
  local tmp_file
  tmp_file="$(mktemp)"

  if grep -q "^${key}=" "$ENV_FILE"; then
    awk -v k="$key" -v v="$value" '
      $0 ~ ("^" k "=") { print k "=" v; next }
      { print }
    ' "$ENV_FILE" >"$tmp_file"
  else
    cat "$ENV_FILE" >"$tmp_file"
    printf "\n%s=%s\n" "$key" "$value" >>"$tmp_file"
  fi

  mv "$tmp_file" "$ENV_FILE"
}

tmp_dir="$(mktemp -d)"
private_key_pem="$tmp_dir/snowflake_rsa_key.p8"
public_key_pem="$tmp_dir/snowflake_rsa_key.pub"
trap 'rm -rf "$tmp_dir"' EXIT

echo "Generating Snowflake RSA key pair"
openssl genrsa 2048 | openssl pkcs8 -topk8 -inform PEM -outform PEM -nocrypt >"$private_key_pem"
openssl rsa -in "$private_key_pem" -pubout -out "$public_key_pem" >/dev/null 2>&1

public_key_clean="$(awk 'NR > 1 && !/END PUBLIC KEY/ { printf "%s", $0 }' "$public_key_pem")"
private_key_b64="$(
  openssl pkcs8 -topk8 -inform PEM -outform DER -in "$private_key_pem" -nocrypt \
    | base64 \
    | tr -d '\n'
)"

snowflake_account_id="${SNOWFLAKE_ACCOUNT_IDENTIFIER:-${SNOWFLAKE_ORGANIZATION_NAME}-${SNOWFLAKE_ACCOUNT}}"

echo "Updating RSA public key for Snowflake user: $SNOWFLAKE_USER"
SNOWSQL_PWD="$SNOWFLAKE_PASSWORD" snowsql \
  -a "$snowflake_account_id" \
  -u "$SNOWFLAKE_USER" \
  -r "$SNOWFLAKE_ROLE" \
  -w "$SNOWFLAKE_WAREHOUSE" \
  -d "$SNOWFLAKE_DATABASE" \
  -s "$SNOWFLAKE_SCHEMA" \
  -q "ALTER USER \"$SNOWFLAKE_USER\" SET RSA_PUBLIC_KEY='$public_key_clean';" \
  -o log_level=ERROR \
  -o exit_on_error=true

echo "Updating .env with SNOWFLAKE_PRIVATE_KEY"
upsert_env "SNOWFLAKE_PRIVATE_KEY" "$private_key_b64"
upsert_env "SNOWFLAKE_PRIVATE_KEY_PASSPHRASE" ""

echo "Done. .env now contains Snowflake key-pair credentials."
