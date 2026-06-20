import asyncio
import json
import logging
import uuid
from asyncio import Future
from typing import Any

from aiohttp import ClientSession, ClientWebSocketResponse, WebSocketError

from . import CommandFailure, WebsocketFailure
from .web_socket_containers import (
    AnovaCommand,
    APCWifiDevice,
    build_a3_payload,
    build_a6_a7_payload,
    build_wifi_cooker_state_body,
)

_LOGGER = logging.getLogger(__name__)

# How long to wait for a RESPONSE to a sent command before raising CommandFailure.
COMMAND_TIMEOUT = 10


class AnovaWebsocketHandler:
    def __init__(self, firebase_jwt: str, jwt: str, session: ClientSession):
        self._firebase_jwt = firebase_jwt
        self.jwt = jwt
        self.session = session
        self.url = f"https://devices.anovaculinary.io/?token={self._firebase_jwt}&supportedAccessories=APC&platform=android"  # noqa
        self.devices: dict[str, APCWifiDevice] = {}
        self.ws: ClientWebSocketResponse | None = None
        self._message_listener: Future[None] | None = None
        # Requests awaiting a matching RESPONSE message, keyed by requestId.
        self._pending_commands: dict[str, Future[None]] = {}

    async def connect(self) -> None:
        try:
            self.ws = await self.session.ws_connect(self.url)
        except WebSocketError as ex:
            raise WebsocketFailure("Failed to connect to the websocket") from ex
        self._message_listener = asyncio.ensure_future(self.message_listener())

    async def disconnect(self) -> None:
        if self.ws is not None:
            await self.ws.close()
        if self._message_listener is not None:
            self._message_listener.cancel()

    async def send_command(
        self, command: AnovaCommand, payload: dict[str, Any]
    ) -> None:
        """Send a command and wait for the device to acknowledge it via RESPONSE.

        The requestId/RESPONSE correlation scheme is inferred from the RESPONSE
        entry in AnovaCommand and has not been confirmed against a packet
        capture of a real command exchange - verify before depending on this
        against a real device.
        """
        if self.ws is None:
            raise WebsocketFailure("Cannot send a command, the websocket is not connected.")
        request_id = str(uuid.uuid4())
        future: Future[None] = asyncio.get_event_loop().create_future()
        self._pending_commands[request_id] = future
        try:
            await self.ws.send_json(
                {"command": command.value, "requestId": request_id, "payload": payload}
            )
            async with asyncio.timeout(COMMAND_TIMEOUT):
                await future
        except TimeoutError as ex:
            raise CommandFailure(
                f"Timed out waiting for a response to {command.value}"
            ) from ex
        finally:
            self._pending_commands.pop(request_id, None)

    def on_message(self, message: dict[str, Any]) -> None:
        _LOGGER.debug("Found message %s", message)
        if message["command"] == AnovaCommand.EVENT_APC_WIFI_LIST:
            payload = message["payload"]
            for device in payload:
                if device["cookerId"] not in self.devices:
                    self.devices[device["cookerId"]] = APCWifiDevice(
                        cooker_id=device["cookerId"],
                        type=device["type"],
                        paired_at=device["pairedAt"],
                        name=device["name"],
                        send_command=self.send_command,
                    )
        elif message["command"] == AnovaCommand.EVENT_APC_STATE:
            cooker_id = message["payload"]["cookerId"]
            if cooker_id not in self.devices:
                pass
            if (ul := self.devices[cooker_id].update_listener) is not None:
                if "job" in message["payload"]["state"]:
                    update = build_wifi_cooker_state_body(
                        message["payload"]["state"]
                    ).to_apc_update()
                elif message["payload"]["type"] == "a3":
                    update = build_a3_payload(message["payload"]["state"])
                elif message["payload"]["type"] in {"a6", "a7"}:
                    update = build_a6_a7_payload(message["payload"]["state"])
                else:
                    return
                ul(update)
        elif message["command"] == AnovaCommand.RESPONSE:
            self._resolve_pending_command(message)

    def _resolve_pending_command(self, message: dict[str, Any]) -> None:
        request_id = message.get("requestId")
        future = self._pending_commands.get(request_id)
        if future is None or future.done():
            return
        payload = message.get("payload") or {}
        if payload.get("success", True):
            future.set_result(None)
        else:
            future.set_exception(CommandFailure(f"Command was rejected: {payload}"))

    async def message_listener(self) -> None:
        if self.ws is not None:
            async for msg in self.ws:
                self.on_message(json.loads(msg.data))
