from unittest.mock import AsyncMock

import pytest

from anova_wifi.web_socket_containers import APCWifiDevice
from anova_wifi.websocket_handler import (
    WEBSOCKET_HEARTBEAT_SECONDS,
    AnovaWebsocketHandler,
)


@pytest.mark.asyncio
async def test_connect_passes_heartbeat_to_ws_connect() -> None:
    """Without a heartbeat, aiohttp can't detect a silently dead connection."""
    session = AsyncMock()
    handler = AnovaWebsocketHandler(
        firebase_jwt="firebase_jwt", jwt="jwt", session=session
    )

    await handler.connect()

    session.ws_connect.assert_awaited_once_with(
        handler.url, heartbeat=WEBSOCKET_HEARTBEAT_SECONDS
    )


def test_state_push_caches_last_update_without_a_listener() -> None:
    """APCWifiDevice.available_commands needs last_update even with no
    update_listener attached, e.g. before HA has finished setting one up."""
    handler = AnovaWebsocketHandler(
        firebase_jwt="firebase_jwt", jwt="jwt", session=AsyncMock()
    )
    device = APCWifiDevice(cooker_id="x", type="pro", paired_at="now", name="test")
    handler.devices["x"] = device
    assert device.update_listener is None

    handler.on_message(
        {
            "command": "EVENT_APC_STATE",
            "payload": {
                "cookerId": "x",
                "type": "pro",
                "state": {
                    "job": {
                        "cook-time-seconds": 0,
                        "id": "job-id",
                        "mode": "COOK",
                        "ota-url": "",
                        "target-temperature": 60,
                        "temperature-unit": "C",
                    },
                    "job-status": {
                        "cook-time-remaining": 0,
                        "job-start-systick": 0,
                        "provisioning-pairing-code": 0,
                        "state": "COOKING",
                        "state-change-systick": 0,
                    },
                    "pin-info": {},
                    "temperature-info": {"water-temperature": 25.0},
                },
            },
        }
    )

    assert device.last_update is not None
    assert device.is_cooking is True
