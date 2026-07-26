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

## Command payload field names

`build_set_target_temperature_payload` and `build_stop_cook_payload` use
`cookerId`/`targetTemperature`/`temperatureUnit` field names. `build_start_cook_payload`
and `build_set_timer_payload` use `cookerId`/`type`/`unit`/`timer`, matching
Anova's documented Wi-Fi command schema (see
[developer.anovaculinary.com/docs/devices/wifi/sous-vide-commands](https://developer.anovaculinary.com/docs/devices/wifi/sous-vide-commands)).
This shape is universal across device types — there is no per-type variation
to branch on.

The `requestId`/`RESPONSE` correlation scheme in
`AnovaWebsocketHandler.send_command` is confirmed: the server echoes a
`RESPONSE` message with the same `requestId` for every command in this file.

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
