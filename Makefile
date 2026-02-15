SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: \
	help help-setup help-infra \
	setup.create-env setup.provision-snowflake setup.local-development-environment \
	infra.configure-airbyte infra.start-airflow infra.start-websocket \
	infra.start-kafka-connect infra.configure-snowflake-kafka-sink infra.generate-snowflake-keypair infra.up infra.up-all infra.down \
	infra.create-streaming-dynamic-tables \
	create-env provision-snowflake setup-local-environment \
	configure-airbyte start-airflow start-websocket \
	start-kafka-connect configure-snowflake-kafka-sink generate-snowflake-keypair create-streaming-dynamic-tables start-local-infra run-local-environment start-all-infra \
	stop-local-infra stop-local-containers

help: ## Show available target groups
	@echo "Local Development Environment Setup"
	@$(MAKE) --no-print-directory help-setup
	@echo ""
	@echo "Local Infra Actions"
	@$(MAKE) --no-print-directory help-infra

help-setup:
	@awk 'BEGIN {FS = ":.*##"} /^setup\.[a-zA-Z0-9._-]+:.*##/ {printf "  \033[36m%-36s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

help-infra:
	@awk 'BEGIN {FS = ":.*##"} /^infra\.[a-zA-Z0-9._-]+:.*##/ {printf "  \033[36m%-36s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

setup.create-env: ## Create .env with Snowflake and local settings
	bash ./scripts/setup/create_env.sh

setup.provision-snowflake: ## Provision Snowflake infrastructure via Terraform
	bash ./scripts/setup/create_snowflake_role.sh
	bash ./scripts/setup/provision_snowflake_remote.sh

setup.local-development-environment: ## Run full setup (env -> snowflake)
	$(MAKE) setup.create-env
	$(MAKE) setup.provision-snowflake

infra.configure-airbyte: ## Configure Airbyte source/destination/connections
	bash ./scripts/infra/configure_airbyte.sh

infra.start-airflow: ## Start local Airflow
	bash ./scripts/infra/start_airflow.sh

infra.start-websocket: ## Start websocket producer container
	bash ./scripts/infra/start_web_socket.sh

infra.start-kafka-connect: ## Start local Kafka + Kafka Connect
	bash ./scripts/infra/start_kafka_connect.sh

infra.configure-snowflake-kafka-sink: ## Register Snowflake sink connector for trade topic
	bash ./scripts/infra/configure_snowflake_kafka_sink.sh

infra.generate-snowflake-keypair: ## Generate key-pair auth, alter Snowflake user, and update .env
	bash ./scripts/infra/generate_snowflake_keypair.sh

infra.create-streaming-dynamic-tables: ## Create/replace Snowflake Dynamic Tables for streaming silver/gold
	bash ./scripts/infra/create_streaming_dynamic_tables.sh

infra.up: ## Start local infra (airbyte -> configure -> airflow)
	bash ./scripts/infra/start_local_infra.sh

infra.up-all: ## Start full local infra (infra.up + kafka connect + snowflake sink + websocket)
	bash ./scripts/infra/start_all_infra.sh

infra.down: ## Stop local containers and remove local volumes
	bash ./scripts/infra/stop_local_infra.sh

# Backward-compatible aliases
create-env: setup.create-env
provision-snowflake: setup.provision-snowflake
setup-local-environment: setup.local-development-environment

configure-airbyte: infra.configure-airbyte
start-airflow: infra.start-airflow
start-websocket: infra.start-websocket
start-kafka-connect: infra.start-kafka-connect
configure-snowflake-kafka-sink: infra.configure-snowflake-kafka-sink
generate-snowflake-keypair: infra.generate-snowflake-keypair
create-streaming-dynamic-tables: infra.create-streaming-dynamic-tables
start-local-infra: infra.up
run-local-environment: infra.up
start-all-infra: infra.up-all
stop-local-infra: infra.down
stop-local-containers: infra.down
