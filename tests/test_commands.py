import asyncio
from unittest.mock import AsyncMock

import pytest

from anova_wifi import AnovaCommand, APCWifiDevice, CommandFailure, WebsocketFailure
from anova_wifi.mocks.anova_api import DUMMY_ID, anova_api_mock
from anova_wifi.websocket_handler import AnovaWebsocketHandler

pytestmark = pytest.mark.asyncio


def _make_handler() -> AnovaWebsocketHandler:
    handler = AnovaWebsocketHandler("fb_jwt", "jwt", AsyncMock())
    handler.ws = AsyncMock()
    return handler


async def _respond_to_pending_command(
    handler: AnovaWebsocketHandler, success: bool
) -> None:
    """Simulate the device replying to whatever command was just sent."""
    await asyncio.sleep(0)
    sent_payload = handler.ws.send_json.call_args.args[0]
    handler.on_message(
        {
            "command": "RESPONSE",
            "requestId": sent_payload["requestId"],
            "payload": {"success": success},
        }
    )


async def test_send_command_resolves_on_successful_response() -> None:
    handler = _make_handler()
    asyncio.ensure_future(_respond_to_pending_command(handler, success=True))

    await handler.send_command(AnovaCommand.CMD_APC_SET_TARGET_TEMP, {"cookerId": "x"})

    assert handler._pending_commands == {}


async def test_send_command_raises_on_rejected_response() -> None:
    handler = _make_handler()
    asyncio.ensure_future(_respond_to_pending_command(handler, success=False))

    with pytest.raises(CommandFailure):
        await handler.send_command(AnovaCommand.CMD_APC_STOP, {"cookerId": "x"})


async def test_send_command_raises_when_not_connected() -> None:
    handler = AnovaWebsocketHandler("fb_jwt", "jwt", AsyncMock())

    with pytest.raises(WebsocketFailure):
        await handler.send_command(AnovaCommand.CMD_APC_STOP, {"cookerId": "x"})


async def test_send_command_times_out(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("anova_wifi.websocket_handler.COMMAND_TIMEOUT", 0.01)
    handler = _make_handler()

    with pytest.raises(CommandFailure):
        await handler.send_command(AnovaCommand.CMD_APC_STOP, {"cookerId": "x"})


async def test_device_without_handler_raises() -> None:
    device = APCWifiDevice(cooker_id="x", type="a5", paired_at="now", name="test")

    with pytest.raises(WebsocketFailure):
        await device.stop_cook()


async def test_device_set_target_temperature_sends_expected_payload() -> None:
    api = anova_api_mock()
    await api.authenticate()
    await api.create_websocket()
    device = api.websocket_handler.devices[DUMMY_ID]

    await device.set_target_temperature(60.0, "C")

    assert api.websocket_handler.sent_commands == [
        {
            "command": "CMD_APC_SET_TARGET_TEMP",
            "payload": {
                "cookerId": DUMMY_ID,
                "targetTemperature": 60.0,
                "temperatureUnit": "C",
            },
        }
    ]


async def test_device_start_cook_sends_expected_payload() -> None:
    api = anova_api_mock()
    await api.authenticate()
    await api.create_websocket()
    device = api.websocket_handler.devices[DUMMY_ID]

    await device.start_cook(60.0, 3600, "C")

    assert api.websocket_handler.sent_commands == [
        {
            "command": "CMD_APC_START",
            "payload": {
                "cookerId": DUMMY_ID,
                "targetTemperature": 60.0,
                "cookTimeSeconds": 3600,
                "temperatureUnit": "C",
            },
        }
    ]


async def test_device_stop_cook_sends_expected_payload() -> None:
    api = anova_api_mock()
    await api.authenticate()
    await api.create_websocket()
    device = api.websocket_handler.devices[DUMMY_ID]

    await device.stop_cook()

    assert api.websocket_handler.sent_commands == [
        {"command": "CMD_APC_STOP", "payload": {"cookerId": DUMMY_ID}}
    ]


async def test_device_set_timer_sends_expected_payload() -> None:
    api = anova_api_mock()
    await api.authenticate()
    await api.create_websocket()
    device = api.websocket_handler.devices[DUMMY_ID]

    await device.set_timer(900)

    assert api.websocket_handler.sent_commands == [
        {
            "command": "CMD_APC_SET_TIMER",
            "payload": {"cookerId": DUMMY_ID, "cookTimeSeconds": 900},
        }
    ]


async def test_device_command_failure_propagates() -> None:
    api = anova_api_mock(fail_commands=True)
    await api.authenticate()
    await api.create_websocket()
    device = api.websocket_handler.devices[DUMMY_ID]

    with pytest.raises(CommandFailure):
        await device.stop_cook()
