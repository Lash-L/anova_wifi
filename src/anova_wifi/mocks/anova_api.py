import asyncio
import json
from dataclasses import dataclass
from typing import Any
from unittest.mock import AsyncMock

from aiohttp import ClientSession

from anova_wifi import AnovaWebsocketHandler, NoDevicesFound

DUMMY_ID = "anova_id"


@dataclass
class MockedanovaWebsocketMessage:
    input_data: dict[str, Any]
    data: str = ""

    def __post_init__(self) -> None:
        self.data = json.dumps(self.input_data)


class MockedAnovaWebsocketStream:
    def __init__(self, messages: list[MockedanovaWebsocketMessage]):
        self.messages = messages

    def __aiter__(self) -> "MockedAnovaWebsocketStream":
        return self

    async def __anext__(self) -> MockedanovaWebsocketMessage:
        """Get the next message in the websocket stream."""
        if self.messages:
            return self.messages.pop(0)
        else:
            raise StopAsyncIteration

    def clear(self) -> None:
        """Clear the Websocket stream."""
        self.messages.clear()


class MockedAnovaWebsocketHandler(AnovaWebsocketHandler):
    def __init__(
        self,
        firebase_jwt: str,
        jwt: str,
        session: ClientSession,
        connect_messages: list[MockedanovaWebsocketMessage],
        post_connect_messages: list[MockedanovaWebsocketMessage],
    ):
        super().__init__(firebase_jwt, jwt, session)
        self.connect_messages = connect_messages
        self.post_connect_messages = post_connect_messages

    async def connect(self) -> None:
        """Create a future for the message listener."""
        self.ws = MockedAnovaWebsocketStream(self.connect_messages)
        await self.message_listener()
        self.ws = MockedAnovaWebsocketStream(self.post_connect_messages)
        asyncio.ensure_future(self.message_listener())


def anova_api_mock(
    connect_messages: list[MockedanovaWebsocketMessage] | None = None,
    post_connect_messages: list[MockedanovaWebsocketMessage] | None = None,
) -> AsyncMock:
    """Mock the api for Anova."""
    api_mock = AsyncMock()

    async def authenticate_side_effect() -> None:
        api_mock.jwt = "my_test_jwt"
        api_mock._firebase_jwt = "my_test_firebase_jwt"

    async def create_websocket_side_effect() -> None:
        api_mock.websocket_handler = MockedAnovaWebsocketHandler(
            firebase_jwt=api_mock._firebase_jwt,
            jwt=api_mock.jwt,
            session=AsyncMock(),
            connect_messages=connect_messages
            if connect_messages is not None
            else [
                MockedanovaWebsocketMessage(
                    {
                        "command": "EVENT_APC_WIFI_LIST",
                        "payload": [
                            {
                                "cookerId": DUMMY_ID,
                                "type": "a5",
                                "pairedAt": "2023-08-12T02:33:20.917716Z",
                                "name": "Anova Precision Cooker",
                            }
                        ],
                    }
                ),
            ],
            post_connect_messages=post_connect_messages
            if post_connect_messages is not None
            else [
                MockedanovaWebsocketMessage(
                    {
                        "command": "EVENT_APC_STATE",
                        "payload": {
                            "cookerId": DUMMY_ID,
                            "state": {
                                "boot-id": "8620610049456548422",
                                "job": {
                                    "cook-time-seconds": 0,
                                    "id": "8759286e3125b0c547",
                                    "mode": "IDLE",
                                    "ota-url": "",
                                    "target-temperature": 54.72,
                                    "temperature-unit": "F",
                                },
                                "job-status": {
                                    "cook-time-remaining": 0,
                                    "job-start-systick": 599679,
                                    "provisioning-pairing-code": 7514,
                                    "state": "",
                                    "state-change-systick": 599679,
                                },
                                "pin-info": {
                                    "device-safe": 0,
                                    "water-leak": 0,
                                    "water-level-critical": 0,
                                    "water-temp-too-high": 0,
                                },
                                "system-info": {
                                    "class": "A5",
                                    "firmware-version": "2.2.0",
                                    "type": "RA2L1-128",
                                },
                                "system-info-details": {
                                    "firmware-version-raw": "VM178_A_02.02.00_MKE15-128",
                                    "systick": 607026,
                                    "version-string": "VM171_A_02.02.00 RA2L1-128",
                                },
                                "temperature-info": {
                                    "heater-temperature": 22.37,
                                    "triac-temperature": 36.04,
                                    "water-temperature": 18.33,
                                },
                            },
                        },
                    }
                ),
            ],
        )
        await api_mock.websocket_handler.connect()
        if not api_mock.websocket_handler.devices:
            raise NoDevicesFound("No devices were found on the websocket.")

    api_mock.authenticate.side_effect = authenticate_side_effect
    api_mock.create_websocket.side_effect = create_websocket_side_effect
    return api_mock
