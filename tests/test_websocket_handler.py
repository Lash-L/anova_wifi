from datetime import UTC, datetime
from unittest.mock import AsyncMock

from aiohttp import ClientConnectionResetError
import pytest

from anova_wifi.exceptions import WebsocketFailure
from anova_wifi.web_socket_containers import AnovaCommand, APCWifiDevice
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


@pytest.mark.asyncio
async def test_send_command_wraps_connection_reset_as_websocket_failure() -> None:
    """A dying transport races the reconnect logic - send_json can raise
    ClientConnectionResetError even though self.ws is still set. Callers
    only handle WebsocketFailure/CommandFailure, so the raw aiohttp
    exception must be wrapped rather than propagated as-is."""
    handler = AnovaWebsocketHandler(
        firebase_jwt="firebase_jwt", jwt="jwt", session=AsyncMock()
    )
    handler.ws = AsyncMock()
    handler.ws.send_json.side_effect = ClientConnectionResetError(
        "Cannot write to closing transport"
    )

    with pytest.raises(WebsocketFailure):
        await handler.send_command(AnovaCommand.CMD_APC_STOP, {})


def test_state_push_caches_last_update_without_a_listener() -> None:
    """APCWifiDevice.available_commands needs last_update even with no
    update_listener attached, e.g. before HA has finished setting one up."""
    handler = AnovaWebsocketHandler(
        firebase_jwt="firebase_jwt", jwt="jwt", session=AsyncMock()
    )
    device = APCWifiDevice(cooker_id="x", type="pro", paired_at="now", name="test")
    handler.devices["x"] = device
    assert device.update_listener is None
    assert device.last_update_received_at is None

    before = datetime.now(UTC)
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
    assert device.last_update_received_at is not None
    assert before <= device.last_update_received_at <= datetime.now(UTC)
