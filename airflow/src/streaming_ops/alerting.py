import json
import os
from urllib.request import Request, urlopen


class SlackNotifier:
    def __init__(self, webhook_url: str | None = None) -> None:
        self.webhook_url = webhook_url or os.getenv("SLACK_WEBHOOK_URL", "")

    def send(self, message: str) -> None:
        if not self.webhook_url:
            return

        req = Request(
            self.webhook_url,
            data=json.dumps({"text": message}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urlopen(req, timeout=10) as response:
            if response.status // 100 != 2:
                raise RuntimeError(f"Slack webhook failed with status {response.status}")
