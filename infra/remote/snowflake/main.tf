resource "snowflake_database" "trading_analytics" {
  name = "TRADING_ANALYTICS"
}

resource "snowflake_schema" "bronze" {
  database = snowflake_database.trading_analytics.name
  name     = "BRONZE"
}

resource "snowflake_schema" "silver" {
  database = snowflake_database.trading_analytics.name
  name     = "SILVER"
}

resource "snowflake_schema" "gold" {
  database = snowflake_database.trading_analytics.name
  name     = "GOLD"
}