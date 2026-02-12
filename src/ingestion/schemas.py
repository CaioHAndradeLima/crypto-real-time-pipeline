from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, Optional


@dataclass
class BinanceTradeEvent:
    event_type: str
    event_time: datetime
    symbol: str
    trade_id: int
    price: str
    quantity: str
    buyer_order_id: Optional[int]
    seller_order_id: Optional[int]
    trade_time: datetime
    is_maker: bool
    raw: Dict[str, Any]

    @staticmethod
    def from_payload(payload: Dict[str, Any]) -> "BinanceTradeEvent":
        return BinanceTradeEvent(
            event_type=payload.get("e"),
            event_time=datetime.fromtimestamp(payload["E"] / 1000),
            symbol=payload.get("s"),
            trade_id=payload.get("t"),
            price=payload.get("p"),
            quantity=payload.get("q"),
            buyer_order_id=payload.get("b"),
            seller_order_id=payload.get("a"),
            trade_time=datetime.fromtimestamp(payload["T"] / 1000),
            is_maker=payload.get("m"),
            raw=payload,
        )
