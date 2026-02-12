SHELL := /bin/bash

.DEFAULT_GOAL := help

.PHONY: help create-env provision-snowflake configure-dbt-profile setup-local-environment

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
