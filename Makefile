SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: \
	help help-setup help-infra \
	setup.check-dev-deps setup.create-env setup.provision-snowflake setup.generate-keypair setup.create-dynamic-tables \
	setup.from-scratch \
	infra.start-airflow infra.start-kafka-connect infra.configure-snowflake-kafka-sink infra.start-websocket \
	infra.up infra.up-all infra.from-scratch infra.down \
	create-env provision-snowflake start-airflow start-kafka-connect configure-snowflake-kafka-sink start-websocket \
	start-local-infra start-all-infra run-local-environment stop-local-infra stop-local-containers

help: ## Show available target groups
	@echo "Setup Commands"
	@$(MAKE) --no-print-directory help-setup
	@echo ""
	@echo "Infra Commands"
	@$(MAKE) --no-print-directory help-infra

help-setup:
	@awk 'BEGIN {FS = ":.*##"} /^setup\.[a-zA-Z0-9._-]+:.*##/ {printf "  \033[36m%-34s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

help-infra:
	@awk 'BEGIN {FS = ":.*##"} /^infra\.[a-zA-Z0-9._-]+:.*##/ {printf "  \033[36m%-34s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

# -----------------------------
# Setup
# -----------------------------

setup.check-dev-deps: ## Verify/install local developer dependencies (Python3, Docker, Terraform, SnowSQL)
	bash ./scripts/setup/check_dev_dependencies.sh

setup.create-env: ## Create .env with Snowflake and local settings
	bash ./scripts/setup/create_env.sh

setup.provision-snowflake: ## Provision Snowflake resources (roles, database, schemas, warehouse, grants)
	bash ./scripts/setup/create_snowflake_role.sh
	bash ./scripts/setup/provision_snowflake_remote.sh

setup.generate-keypair: ## Generate Snowflake key-pair auth and update .env
	bash ./scripts/infra/generate_snowflake_keypair.sh

setup.create-dynamic-tables: ## Create/replace streaming Dynamic Tables (silver/gold)
	bash ./scripts/infra/create_streaming_dynamic_tables.sh

setup.from-scratch: ## Full setup from zero for a new machine/account
	$(MAKE) setup.check-dev-deps
	$(MAKE) setup.create-env
	$(MAKE) setup.provision-snowflake
	$(MAKE) setup.generate-keypair
	$(MAKE) setup.create-dynamic-tables

# -----------------------------
# Infra Run
# -----------------------------

infra.start-airflow: ## Start local Airflow stack
	bash ./scripts/infra/start_airflow.sh

infra.start-kafka-connect: ## Start Kafka + Kafka Connect stack
	bash ./scripts/infra/start_kafka_connect.sh

infra.configure-snowflake-kafka-sink: ## Register/update Snowflake sink connector
	bash ./scripts/infra/configure_snowflake_kafka_sink.sh

infra.start-websocket: ## Start Binance websocket producer container
	bash ./scripts/infra/start_web_socket.sh

infra.up: ## Start baseline infra (Airflow)
	bash ./scripts/infra/start_local_infra.sh

infra.up-all: ## Start full runtime infra (airflow + kafka/connect + sink + websocket)
	bash ./scripts/infra/start_all_infra.sh

infra.from-scratch: ## Full infra run from zero for a new machine/account
	$(MAKE) infra.down
	$(MAKE) infra.up-all

infra.down: ## Stop local containers and remove local volumes
	bash ./scripts/infra/stop_local_infra.sh

infra.restart: ## Restart infra calling infra.down, infra.up-all
	$(MAKE) infra.down
	$(MAKE) infra.up-all

# -----------------------------
# Backward-compatible aliases
# -----------------------------

create-env: setup.create-env
provision-snowflake: setup.provision-snowflake
start-airflow: infra.start-airflow
start-kafka-connect: infra.start-kafka-connect
configure-snowflake-kafka-sink: infra.configure-snowflake-kafka-sink
start-websocket: infra.start-websocket
start-local-infra: infra.up
run-local-environment: infra.up
start-all-infra: infra.up-all
stop-local-infra: infra.down
stop-local-containers: infra.down
