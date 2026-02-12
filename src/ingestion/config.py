import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
KAFKA_TOPIC_TRADES = os.getenv("KAFKA_TOPIC_TRADES", "crypto_trades")

BINANCE_WS_BASE_URL = "wss://stream.binance.com:9443/ws"
SYMBOLS = os.getenv("BINANCE_SYMBOLS", "btcusdt").split(",")
