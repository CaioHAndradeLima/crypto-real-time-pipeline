resource "snowflake_grant_privileges_to_account_role" "bronze_usage" {
  privileges        = ["USAGE"]
  account_role_name = var.snowflake_role

  on_schema {
    schema_name = "\"${snowflake_database.trading_analytics.name}\".\"${snowflake_schema.bronze.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "bronze_create_table" {
  privileges        = ["CREATE TABLE"]
  account_role_name = var.snowflake_role

  on_schema {
    schema_name = "\"${snowflake_database.trading_analytics.name}\".\"${snowflake_schema.bronze.name}\""
  }
}

resource "snowflake_grant_privileges_to_account_role" "trading_wh_usage" {
  privileges        = ["USAGE"]
  account_role_name = var.snowflake_role

  on_account_object {
    object_type = "WAREHOUSE"
    object_name = "\"${snowflake_warehouse.trading_wh.name}\""
  }

  depends_on = [
    snowflake_warehouse.trading_wh
  ]
}
