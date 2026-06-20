# Sending commands to a device

Implements [#33](https://github.com/Lash-L/anova_wifi/issues/33). This library
was originally read-only; this note records the design decisions made when
adding write support, and why, particularly for consumers integrating this
into Home Assistant.

## Where command methods live: on `APCWifiDevice`, not the handler or a new client class

`set_target_temperature`, `start_cook`, `stop_cook`, and `set_timer` are methods
on `APCWifiDevice` (`web_socket_containers.py`), not on `AnovaWebsocketHandler`
or a separate command-sender object.

**Why:** Home Assistant's coordinator pattern exposes one "device" object per
entity (`coordinator.device` in most Platinum-tier integrations, e.g.
`pylamarzocco`'s `LaMarzoccoMachine`), and entities call command methods
directly on that object — `self.coordinator.device.set_coffee_target_temperature(...)`.
Home Assistant's `AnovaCoordinator` already exposes `coordinator.anova_device`,
an `APCWifiDevice`. Putting the command methods there means HA entities can
call `self.coordinator.anova_device.set_target_temperature(...)` with no new
plumbing in the coordinator — the coordinator stays a thin data-refresh layer,
matching how other cloud-polling/push integrations in HA core are structured.

The alternative (a coordinator-side wrapper method per command) would put
business logic in the integration that belongs in the library, and would
diverge from the convention every other Platinum-tier cloud integration in HA
core follows.

## How `APCWifiDevice` reaches the websocket: injected callback, not a back-reference

`APCWifiDevice` gets a `send_command` callable injected by
`AnovaWebsocketHandler` when the device is discovered (`on_message`), rather
than holding a reference to the handler itself.

**Why:** `APCWifiDevice` is defined in `web_socket_containers.py`, which
`websocket_handler.py` already imports from. A direct reference back to
`AnovaWebsocketHandler` would create a circular import. This also mirrors the
existing `update_listener` field on the same dataclass — that's already a
callback injected by the handler for push updates, so `send_command` follows
the same shape for the write path.

## Response correlation: `requestId` + a pending-futures map

`send_command` generates a `requestId`, sends it alongside the command, and
`await`s an `asyncio.Future` that `on_message` resolves when a matching
`RESPONSE` message arrives. A timeout raises `CommandFailure`.

**Why:** Without this, command calls would be fire-and-forget — the HA entity
that called `await device.stop_cook()` would have no way to know whether the
cooker accepted the command, and Home Assistant has no path to surface a
clean error to the user (a switch that silently fails to turn off is a bad UX
and a support burden). Correlating responses lets the HA entity layer
translate failures into `HomeAssistantError` synchronously, in the same call
that the user triggered, which is the pattern every Platinum-tier integration
with a write path uses (`pylamarzocco`'s `RequestNotSuccessful`, etc.).

## ⚠️ Unverified: command payload field names and the `RESPONSE`/`requestId` shape

The receive-side payload shapes in this library (`build_a3_payload`, etc.)
were derived from captured app traffic and are trustworthy. The **outgoing**
command shapes (`build_set_target_temperature_payload` and friends) and the
`requestId`/`RESPONSE` correlation scheme are inferred from the `AnovaCommand`
enum values that were "grabbed from apk" (see the comment in
`web_socket_containers.py`) — they have not been confirmed against a packet
capture of a real command exchange.

**Before relying on this against a real device**, capture real traffic from
the official Anova app (e.g. with mitmproxy) sending a `CMD_APC_SET_TARGET_TEMP`
/ `CMD_APC_START` / `CMD_APC_STOP` and confirm:
- the exact payload field names/casing for each command
- whether the device actually echoes a `RESPONSE` with the same `requestId`,
  or whether success is only ever signaled by the next `EVENT_APC_STATE` push

If the device doesn't echo `requestId`, the correlation logic in
`AnovaWebsocketHandler.send_command` will need to change to either drop
correlation (fire-and-forget, relying on the next state push) or correlate on
`cookerId` + command type instead.

## What this means for the Home Assistant integration

- Entities should call `self.coordinator.anova_device.<command>(...)` directly
  in their `async_turn_on`/`async_turn_off`/`async_set_native_value`, not go
  through a coordinator wrapper method.
- Catch `CommandFailure` (and `WebsocketFailure`, if the websocket has dropped)
  in the entity and re-raise as a translated `HomeAssistantError`
  (`translation_domain`/`translation_key`/`translation_placeholders`, defined
  in `strings.json`'s `exceptions` block) — see `pylamarzocco`'s `switch.py`/
  `number.py` for the exact shape to copy.
- Call `self.async_write_ha_state()` immediately after a successful command
  rather than waiting for the coordinator's next push; the websocket push that
  follows will reconcile state via the existing `update_listener` wiring.
