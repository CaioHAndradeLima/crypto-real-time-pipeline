
resource "snowflake_warehouse" "trading_wh" {
  name           = "TRADING_WH"
  warehouse_size = "XSMALL"

  auto_suspend = 60
  auto_resume  = true

  initially_suspended = true

  comment = "Warehouse for trading data pipeline (ingestion + analytics)"
}