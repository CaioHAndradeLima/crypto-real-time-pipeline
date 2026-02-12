SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: help create-env provision-snowflake configure-dbt-profile setup-local-environment start-postgres start-airbyte configure-airbyte start-airflow start-local-infra run-local-environment stop-local-infra stop-local-containers

help: ## Show available targets
	@awk 'BEGIN {FS = ":.*##"} /^[a-zA-Z_-]+:.*##/ {printf "\033[36m%-24s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

create-env: ## Create .env with Snowflake and local settings
	bash ./scripts/setup/create_env.sh

provision-snowflake: ## Provision Snowflake infrastructure via Terraform
	bash ./scripts/setup/provision_snowflake_remote.sh

configure-dbt-profile: ## Create dbt/profiles.yml from .env values
	bash ./scripts/setup/configure_dbt_profile.sh

setup-local-environment: ## Setup local environment (env -> snowflake -> dbt)
	$(MAKE) create-env
	$(MAKE) provision-snowflake
	$(MAKE) configure-dbt-profile

start-postgres: ## Start local Postgres
	bash ./scripts/infra/start_postgres.sh

start-airbyte: ## Start local Airbyte
	bash ./scripts/infra/start_airbyte.sh

configure-airbyte: ## Configure Airbyte source/destination/connections
	bash ./scripts/infra/configure_airbyte.sh

start-airflow: ## Start local Airflow
	bash ./scripts/infra/start_airflow.sh

start-local-infra: ## Start local infra (postgres -> airbyte -> configure -> airflow)
	bash ./scripts/infra/start_local_infra.sh

run-local-environment: start-local-infra ## Alias for start-local-infra

stop-local-infra: ## Stop local containers and remove local volumes
	bash ./scripts/infra/stop_local_infra.sh

stop-local-containers: stop-local-infra ## Alias for stop-local-infra
