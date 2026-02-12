import json
import logging
import time
from kafka import KafkaProducer
from websocket import WebSocketApp

from src.ingestion.config import (
    BINANCE_WS_BASE_URL,
    KAFKA_BOOTSTRAP_SERVERS,
    KAFKA_TOPIC_TRADES,
    SYMBOLS,
)
from src.ingestion.schemas import BinanceTradeEvent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("binance-producer")


def create_kafka_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8"),
        retries=5,
        linger_ms=50,
    )


def on_message(ws, message):
    payload = json.loads(message)

    # Handle combined streams
    if "data" in payload:
        payload = payload["data"]

    try:
        trade = BinanceTradeEvent.from_payload(payload)

        producer.send(
            topic=KAFKA_TOPIC_TRADES,
            key=trade.symbol,
            value=trade.raw,
        )

    except Exception as e:
        logger.exception("Failed to process message", exc_info=e)


def on_error(ws, error):
    logger.error(f"WebSocket error: {error}")


def on_close(ws, *_):
    logger.warning("WebSocket closed. Reconnecting...")
    time.sleep(5)
    start()


def on_open(ws):
    logger.info("Connected to Binance WebSocket")


def start():
    streams = "/".join(f"{s}@trade" for s in SYMBOLS)
    ws_url = f"{BINANCE_WS_BASE_URL}/{streams}"

    ws = WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )

    ws.run_forever()


if __name__ == "__main__":
    producer = create_kafka_producer()
    start()
