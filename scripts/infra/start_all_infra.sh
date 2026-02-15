#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Start full local infra: airflow -> kafka connect -> snowflake sink -> websocket producer"
bash "$SCRIPT_DIR/start_local_infra.sh"
bash "$SCRIPT_DIR/start_kafka_connect.sh"
bash "$SCRIPT_DIR/configure_snowflake_kafka_sink.sh"
bash "$SCRIPT_DIR/start_web_socket.sh"
