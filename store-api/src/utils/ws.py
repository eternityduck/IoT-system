from typing import Set, Dict
from fastapi import WebSocket
import json


class WebSocketClient:
    subscriptions: Dict[int, Set[WebSocket]] = {}

    def __init__(
        self,
    ) -> None:
        self.subscriptions = {}

    async def send_data_to_subscribers(self, user_id: int, data):
        if user_id in self.subscriptions:
            for websocket in self.subscriptions[user_id]:
                await websocket.send_json(json.dumps(data))
