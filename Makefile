SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: \
	help help-setup help-infra \
	setup.create-env setup.provision-snowflake setup.configure-dbt-profile setup.local-development-environment \
	infra.start-postgres infra.start-airbyte infra.configure-airbyte infra.start-airflow \
	infra.start-kafka-connect infra.configure-snowflake-kafka-sink infra.generate-snowflake-keypair infra.up infra.down \
	create-env provision-snowflake configure-dbt-profile setup-local-environment \
	start-postgres start-airbyte configure-airbyte start-airflow \
	start-kafka-connect configure-snowflake-kafka-sink generate-snowflake-keypair start-local-infra run-local-environment \
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

setup.configure-dbt-profile: ## Create dbt/profiles.yml from .env values
	bash ./scripts/setup/configure_dbt_profile.sh

setup.local-development-environment: ## Run full setup (env -> snowflake -> dbt)
	$(MAKE) setup.create-env
	$(MAKE) setup.provision-snowflake
	$(MAKE) setup.configure-dbt-profile

infra.start-postgres: ## Start local Postgres
	bash ./scripts/infra/start_postgres.sh

infra.start-airbyte: ## Start local Airbyte
	bash ./scripts/infra/start_airbyte.sh

infra.configure-airbyte: ## Configure Airbyte source/destination/connections
	bash ./scripts/infra/configure_airbyte.sh

infra.start-airflow: ## Start local Airflow
	bash ./scripts/infra/start_airflow.sh

infra.start-kafka-connect: ## Start local Kafka + Kafka Connect
	bash ./scripts/infra/start_kafka_connect.sh

infra.configure-snowflake-kafka-sink: ## Register Snowflake sink connector for trade topic
	bash ./scripts/infra/configure_snowflake_kafka_sink.sh

infra.generate-snowflake-keypair: ## Generate key-pair auth, alter Snowflake user, and update .env
	bash ./scripts/infra/generate_snowflake_keypair.sh

infra.up: ## Start local infra (postgres -> airbyte -> configure -> airflow)
	bash ./scripts/infra/start_local_infra.sh

infra.down: ## Stop local containers and remove local volumes
	bash ./scripts/infra/stop_local_infra.sh

# Backward-compatible aliases
create-env: setup.create-env
provision-snowflake: setup.provision-snowflake
configure-dbt-profile: setup.configure-dbt-profile
setup-local-environment: setup.local-development-environment

start-postgres: infra.start-postgres
start-airbyte: infra.start-airbyte
configure-airbyte: infra.configure-airbyte
start-airflow: infra.start-airflow
start-kafka-connect: infra.start-kafka-connect
configure-snowflake-kafka-sink: infra.configure-snowflake-kafka-sink
generate-snowflake-keypair: infra.generate-snowflake-keypair
start-local-infra: infra.up
run-local-environment: infra.up
stop-local-infra: infra.down
stop-local-containers: infra.down
