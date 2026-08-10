import logging
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from .exceptions import NoActiveCookError, WebsocketFailure

_LOGGER = logging.getLogger(__name__)

# Distinct unrecognized AnovaState values already warned about - module-level
# (not a class attribute) so it isn't picked up as an Enum member.
_warned_unknown_states: set[object] = set()

# All of the containers would probably be better of using dacite, but since HA sometimes has issues with dacite I am
# doing them manually


@dataclass
class APCUpdateBinary:
    cooking: bool
    preheating: bool | None = None
    maintaining: bool | None = None
    device_safe: bool | None = None
    water_leak: bool | None = None
    water_level_critical: bool | None = None
    water_temp_too_high: bool | None = None
    water_level_low: bool | None = None


@dataclass
class APCUpdateSensor:
    cook_time: int | None = None
    mode: str | None = None
    state: str | None = None
    a3_state: str | None = None
    target_temperature: float | None = None
    cook_time_remaining: int | None = None
    # Seconds spent in the post-cook keep-warm phase (state MAINTAINING/
    # TIMER_EXPIRED). The device keeps counting job_status.cook-time-remaining
    # upward once the timer hits zero rather than resetting it, so it's split
    # out here instead of being reported as a countdown that counts up.
    time_maintaining: int | None = None
    firmware_version: str | None = None
    heater_temperature: float | None = None
    triac_temperature: float | None = None
    water_temperature: float | None = None


@dataclass
class APCUpdate:
    binary_sensor: APCUpdateBinary
    sensor: APCUpdateSensor


class AnovaMode(str, Enum):
    startup = "STARTUP"
    idle = "IDLE"
    cook = "COOK"
    low_water = "LOW WATER"
    ota = "OTA"
    provisioning = "PROVISIONING"
    high_temp = "HIGH TEMP"
    device_failure = "DEVICE FAILURE"


class AnovaState(str, Enum):
    preheating = "PREHEATING"
    cooking = "COOKING"
    maintaining = "MAINTAINING"
    timer_expired = "TIMER EXPIRED"
    set_timer = "SET TIMER"
    # The device's boot-time idle state: powered on and ready to start a
    # cook, not yet mid-job. Confirmed against a real device push that HA's
    # message listener previously crashed on, having never seen this value.
    ready_to_cook = "START_COOK"
    no_state = ""
    # Anova's developer docs don't enumerate job-status.state values at all,
    # so unrecognized ones (a hypothetical STOP_COOK, or any future addition)
    # must not crash the websocket listener - fall back to this instead.
    unknown = "UNKNOWN"

    @classmethod
    def _missing_(cls, value: object) -> "AnovaState":
        # Pushed on every state message (~2s cadence) while a device is
        # sending an unrecognized value - warn once per distinct value, not
        # once per message, or this floods the log forever.
        if value not in _warned_unknown_states:
            _warned_unknown_states.add(value)
            _LOGGER.warning("Unrecognized Anova job-status state %r", value)
        return cls.unknown


class AnovaA3State(str, Enum):
    no_state = "none"
    connected = "connected"
    disconnected = "disconnected"
    heating = "heating"
    keeping_warm = "keeping_warm"
    cooking = "cooking"
    reconnecting = "reconnecting"


class AnovaCommand(str, Enum):
    EVENT_APC_WIFI_LIST = "EVENT_APC_WIFI_LIST"
    EVENT_APC_STATE = "EVENT_APC_STATE"
    EVENT_APC_WIFI_VERSION = "EVENT_APC_WIFI_VERSION"
    EVENT_APC_WIFI_ADDED = "EVENT_APC_WIFI_ADDED"
    EVENT_APC_WIFI_REMOVED = "EVENT_APC_WIFI_REMOVED"
    CMD_APC_SET_TARGET_TEMP = "CMD_APC_SET_TARGET_TEMP"
    CMD_APC_SET_TIMER = "CMD_APC_SET_TIMER"
    CMD_APC_START = "CMD_APC_START"
    CMD_APC_STOP = "CMD_APC_STOP"
    RESPONSE = "RESPONSE"

    # Grabbed from apk
    CMD_AUTH_TOKEN = "CMD_AUTH_TOKEN"
    AUTH_TOKEN_V2 = "AUTH_TOKEN_V2"
    CMD_APC_SET_METADATA = "CMD_APC_SET_METADATA"
    CMD_APC_SET_TEMPERATURE_UNIT = "CMD_APC_SET_TEMPERATURE_UNIT"
    CMD_APC_OTA = "CMD_APC_OTA"
    CMD_NAME_WIFI_DEVICE = "CMD_NAME_WIFI_DEVICE"
    CMD_APC_A3_SET_CREDENTIALS = "CMD_APC_A3_SET_CREDENTIALS"
    CMD_APC_REGISTER_PUSH_TOKEN = "CMD_APC_REGISTER_PUSH_TOKEN"
    CMD_APC_START_ICEBATH_MONITORING = "CMD_APC_START_ICEBATH_MONITORING"
    CMD_APC_DISCONNECT = "CMD_APC_DISCONNECT"
    CMD_APC_HEALTHCHECK = "CMD_APC_HEALTHCHECK"


@dataclass
class WifiJob:
    id: str
    cook_time_seconds: int
    target_temperature: float
    temperature_unit: str
    mode: AnovaMode
    ota_url: str


@dataclass
class WifiJobStatus:
    cook_time_remaining: int | None
    state: AnovaState


@dataclass
class WifiPinInfo:
    is_device_safe: bool | None
    is_water_leak: bool | None
    is_water_level_critical: bool | None
    is_water_level_low: bool | None
    water_temp_too_high: bool | None


@dataclass
class WifiSystemInfo:
    firmware_version: str
    class_name: str | None = None
    type: str | None = None


@dataclass
class WifiSystemInfo3220:
    firmware_version: str
    has_real_cert_catalog: str | None = None
    firmware_version_raw: str | None = None
    largest_free_heap_size: int | None = None
    stack_low_level: int | None = None
    stack_low_task: int | None = None
    systick: int | None = None
    total_free_heap_size: int | None = None


@dataclass
class WifiSystemInfoNxp:
    firmware_version: str  # 'version-string'


@dataclass
class WifiTemperatureInfo:
    """Gets temperature info for the device. All in celsius."""

    heater_temperature: float | None
    triac_temperature: float | None
    water_temperature: float


@dataclass
class WifiCookerStateBody:
    audio_control: Any | None
    boot_id: str | None
    cap_touch: Any | None
    heater_control: Any | None
    job: WifiJob
    job_status: WifiJobStatus
    motor_control: Any | None
    network_info: Any | None
    pin_info: WifiPinInfo
    system_info: WifiSystemInfo | None
    system_info_3220: WifiSystemInfo3220 | None
    system_info_nxp: WifiSystemInfoNxp | None
    temperature_info: WifiTemperatureInfo

    @property
    def firmware_version(self) -> str:
        if self.system_info:
            return self.system_info.firmware_version
        if self.system_info_3220:
            return self.system_info_3220.firmware_version
        if self.system_info_nxp:
            return self.system_info_nxp.firmware_version
        else:
            return "unknown"

    def to_apc_update(self) -> APCUpdate:
        is_maintaining = self.job_status.state in (
            AnovaState.maintaining,
            AnovaState.timer_expired,
        )
        sensors = APCUpdateSensor(
            cook_time=self.job.cook_time_seconds,
            mode=self.job.mode.name,
            state=self.job_status.state.name,
            target_temperature=self.job.target_temperature,
            cook_time_remaining=(
                0 if is_maintaining else self.job_status.cook_time_remaining
            ),
            time_maintaining=(
                self.job_status.cook_time_remaining if is_maintaining else 0
            ),
            firmware_version=self.firmware_version,
            heater_temperature=self.temperature_info.heater_temperature,
            triac_temperature=self.temperature_info.triac_temperature,
            water_temperature=self.temperature_info.water_temperature,
        )

        binary_sensors = APCUpdateBinary(
            cooking=bool(self.job.mode == AnovaMode.cook),
            preheating=bool(self.job_status.state == AnovaState.preheating),
            maintaining=bool(
                self.job_status.state == AnovaState.maintaining
                or self.job_status.state == AnovaState.timer_expired
            ),
            device_safe=self.pin_info.is_device_safe,
            water_leak=self.pin_info.is_water_leak,
            water_level_critical=self.pin_info.is_water_level_critical,
            water_temp_too_high=self.pin_info.water_temp_too_high,
            water_level_low=self.pin_info.is_water_level_low,
        )
        return APCUpdate(sensor=sensors, binary_sensor=binary_sensors)


def build_wifi_cooker_state_body(apc_response: dict[str, Any]) -> WifiCookerStateBody:
    system_info = None
    system_info_3220 = None
    system_info_nxp = None
    audio_control = apc_response.get("audio-control")
    boot_id = apc_response.get("boot-id")
    cap_touch = apc_response.get("cap-touch")
    heater_control = apc_response.get("heater-control")
    job_json: dict[str, Any] = apc_response["job"]
    job = WifiJob(
        id=job_json["id"],
        cook_time_seconds=job_json["cook-time-seconds"],
        mode=AnovaMode(job_json["mode"]),
        ota_url=job_json["ota-url"],
        target_temperature=job_json["target-temperature"],
        temperature_unit=job_json["temperature-unit"],
    )
    job_status_json: dict[str, Any] = apc_response["job-status"]
    job_status = WifiJobStatus(
        cook_time_remaining=job_status_json.get("cook-time-remaining"),
        state=AnovaState(job_status_json["state"]),
    )
    network_info = apc_response.get("network-info")
    motor_control = apc_response.get("motor-control")
    pin_info_json: dict[str, int] = apc_response["pin-info"]
    pin_info = WifiPinInfo(
        is_device_safe=(
            bool(pin_info_json["device-safe"])
            if "device-safe" in pin_info_json
            else None
        ),
        is_water_leak=(
            bool(pin_info_json.get("water-leak"))
            if "water-leak" in pin_info_json
            else None
        ),
        is_water_level_critical=(
            bool(pin_info_json.get("water-level-critical"))
            if "water-level-critical" in pin_info_json
            else None
        ),
        is_water_level_low=(
            bool(pin_info_json.get("water-level-low"))
            if "water-level-low" in pin_info_json
            else None
        ),
        water_temp_too_high=(
            bool(pin_info_json.get("water-temp-too-high"))
            if "water-temp-too-high" in pin_info_json
            else None
        ),
    )
    system_info_json: dict[str, str] | None = apc_response.get("system-info")
    if system_info_json is not None:
        system_info = WifiSystemInfo(
            firmware_version=system_info_json["firmware-version"],
            class_name=system_info_json.get("class"),
            type=system_info_json.get("type"),
        )
    system_info_3220_json: dict[str, str] | None = apc_response.get("system-info-3220")
    if system_info_3220_json:
        largest_free_heap_size = system_info_3220_json.get("largest-free-heap-size")
        system_info_3220 = WifiSystemInfo3220(
            firmware_version=system_info_3220_json["firmware-version"],
            has_real_cert_catalog=system_info_3220_json.get("has-real-cert-catalog"),
            firmware_version_raw=system_info_3220_json.get("firmware-version-raw"),
            largest_free_heap_size=(
                int(largest_free_heap_size)
                if largest_free_heap_size is not None
                else None
            ),
            # Too lazy to do these right now.
            # stack_low_level=system_info_3220_json.get("stack-low-level"),
            # stack_low_task=system_info_3220_json.get("stack-low-task"),
            # systick=system_info_3220_json.get("systick"),
            # total_free_heap_size=system_info_3220_json.get("total-free-heap-size"),
        )
    system_info_nxp_json: dict[str, str] | None = apc_response.get("system-info-nxp")
    if system_info_nxp_json:
        system_info_nxp = WifiSystemInfoNxp(
            firmware_version=system_info_nxp_json["version-string"]
        )
    temperature_info_json: dict[str, float] = apc_response["temperature-info"]
    temperature_info = WifiTemperatureInfo(
        heater_temperature=temperature_info_json.get("heater-temperature"),
        water_temperature=temperature_info_json["water-temperature"],
        triac_temperature=temperature_info_json.get("triac-temperature"),
    )
    return WifiCookerStateBody(
        audio_control=audio_control,
        boot_id=boot_id,
        cap_touch=cap_touch,
        heater_control=heater_control,
        job=job,
        job_status=job_status,
        motor_control=motor_control,
        pin_info=pin_info,
        system_info=system_info,
        system_info_3220=system_info_3220,
        system_info_nxp=system_info_nxp,
        temperature_info=temperature_info,
        network_info=network_info,
    )


def build_a3_payload(apc_response: dict[str, Any]) -> APCUpdate:
    firmware_version: str = apc_response["firmwareVersion"]
    is_cooking: bool = apc_response["isCooking"]
    current_temperature: float = apc_response["currentTemperature"]
    target_temperature: float = apc_response["targetTemperature"]
    timer_in_seconds: int = apc_response["timerInSeconds"]
    # unit = apc_response.get("unit")
    # is_timer_running = apc_response.get("isTimerRunning")
    # is_speaker_on = apc_response.get("isSpeakerOn")
    # is_alarm_active = apc_response.get("isAlarmActive")
    # current_job_id = apc_response.get("currentJobID")
    current_job = apc_response.get("currentJob")
    # is_keeping_warm = apc_response.get("isKeepingWarming")
    # is_checking_temperature_for_ice_bath = apc_response.get(
    #     "isCheckingTemperatureForIceBath"
    # )
    # is_monitoring_ice_bath = apc_response.get("isMonitoringIcebath")
    # is_connected = apc_response.get("isConnected")
    if current_job is not None:
        job_stage: str = current_job["jobStage"]
        status = AnovaA3State(job_stage)
    else:
        status = AnovaA3State.no_state
    sensors = APCUpdateSensor(
        a3_state=status.name,
        target_temperature=float(target_temperature),
        cook_time_remaining=int(timer_in_seconds),
        firmware_version=firmware_version,
        water_temperature=float(current_temperature),
    )

    binary_sensors = APCUpdateBinary(
        cooking=bool(is_cooking),
        preheating=bool(status == AnovaState.preheating),
        maintaining=bool(
            status == AnovaState.maintaining or status == AnovaState.timer_expired
        ),
    )
    return APCUpdate(binary_sensors, sensors)


def _parse_anova_timestamp(value: str | None) -> datetime | None:
    if value is None:
        return None
    if value.endswith("Z"):
        value = f"{value[:-1]}+00:00"
    return datetime.fromisoformat(value)


def build_a6_a7_payload(apc_response: dict[str, Any]) -> APCUpdate:
    system_info = apc_response["systemInfo"]
    firmware_version = system_info["firmwareVersion"]
    mode = apc_response["state"]["mode"]
    nodes = apc_response["nodes"]
    timer = nodes["timer"]
    timer_mode = timer.get("mode")
    cook = apc_response.get("cook") or {}
    active_stage_mode = cook.get("activeStageMode")
    cook_time = int(timer.get("initial") or 0)
    cook_time_remaining = 0

    if mode == "cook":
        if timer_mode == "completed":
            state = AnovaState.timer_expired
            cook_time_remaining = 0
        elif active_stage_mode == "entering":
            state = AnovaState.preheating
            cook_time_remaining = cook_time
        elif timer_mode == "running":
            state = AnovaState.cooking
            started_at = _parse_anova_timestamp(timer.get("startedAtTimestamp"))
            updated_at = _parse_anova_timestamp(apc_response.get("updatedTimestamp"))
            if started_at is not None and updated_at is not None:
                elapsed = int((updated_at - started_at).total_seconds())
                cook_time_remaining = max(0, cook_time - elapsed)
            else:
                cook_time_remaining = cook_time
        else:
            state = AnovaState.maintaining
            cook_time_remaining = cook_time
    else:
        state = AnovaState.no_state

    sensors = APCUpdateSensor(
        firmware_version=firmware_version,
        mode=mode,
        state=state.name,
        water_temperature=float(nodes["waterTemperatureSensor"]["current"]["celsius"]),
        target_temperature=float(
            nodes["waterTemperatureSensor"]["setpoint"]["celsius"]
        ),
        cook_time=cook_time,
        cook_time_remaining=cook_time_remaining,
    )
    binary_sensors = APCUpdateBinary(
        cooking=bool(mode == "cook"),
        preheating=bool(state == AnovaState.preheating),
        maintaining=bool(
            state == AnovaState.maintaining or state == AnovaState.timer_expired
        ),
        water_level_low=bool(nodes["lowWater"]["warning"]),
        water_level_critical=bool(nodes["lowWater"]["empty"]),
    )
    return APCUpdate(binary_sensors, sensors)


def build_set_target_temperature_payload(
    cooker_id: str, cooker_type: str, target_temperature: float, temperature_unit: str
) -> dict[str, Any]:
    """Build the payload for CMD_APC_SET_TARGET_TEMP.

    Not part of Anova's published Wi-Fi command schema - inferred from the
    AnovaCommand enum. Confirmed against a real device: while a job is
    actively running, this reliably updates job.target-temperature. While
    idle, the server acks the command but job.target-temperature never
    changes in subsequent state pushes - the official app likely tracks the
    pre-cook target locally and only sends it via CMD_APC_START.
    """
    return {
        "cookerId": cooker_id,
        "type": cooker_type,
        "targetTemperature": target_temperature,
        "unit": temperature_unit,
    }


def build_start_cook_payload(
    cooker_id: str,
    cooker_type: str,
    target_temperature: float,
    cook_time_seconds: int,
    temperature_unit: str,
) -> dict[str, Any]:
    """Build the payload for CMD_APC_START.

    See developer.anovaculinary.com/docs/devices/wifi/sous-vide-commands.
    """
    return {
        "cookerId": cooker_id,
        "type": cooker_type,
        "targetTemperature": target_temperature,
        "unit": temperature_unit,
        "timer": cook_time_seconds,
    }


def build_stop_cook_payload(cooker_id: str, cooker_type: str) -> dict[str, Any]:
    """Build the payload for CMD_APC_STOP.

    See developer.anovaculinary.com/docs/devices/wifi/sous-vide-commands.
    """
    return {"cookerId": cooker_id, "type": cooker_type}


def build_set_timer_payload(
    cooker_id: str, cooker_type: str, cook_time_seconds: int
) -> dict[str, Any]:
    """Build the payload for CMD_APC_SET_TIMER.

    Not part of Anova's published Wi-Fi command schema - inferred from the
    AnovaCommand enum. Confirmed against a real device, including while idle
    (job.cook-time-seconds updates immediately) - APCWifiDevice.update_running_cook
    still requires an active cook for this too, to keep its API scoped to
    "modify the running job" rather than exposing an idle-only timer with no
    clear product meaning.
    """
    return {"cookerId": cooker_id, "type": cooker_type, "timer": cook_time_seconds}


class Capability(str, Enum):
    """A command that a device may or may not support, and/or be valid to call right now."""

    START_COOK = "start_cook"
    STOP_COOK = "stop_cook"
    UPDATE_RUNNING_COOK = "update_running_cook"


# Precision Cooker (APC) device type identifiers, per
# developer.anovaculinary.com/docs/devices/wifi/authentication. All of them
# share the same command schema (see build_start_cook_payload et al.), so
# they all support the same set of commands.
_APC_TYPES = frozenset({"a3", "a4", "a5", "a6", "a7", "a8", "pro"})
_APC_CAPABILITIES = frozenset(Capability)


def get_supported_capabilities(device_type: str) -> frozenset[Capability]:
    """Return the commands supported by a device of the given type, regardless of its current state.

    Unrecognized types (e.g. a future Precision Oven type) report no
    capabilities rather than assuming untested command support.
    """
    if device_type in _APC_TYPES:
        return _APC_CAPABILITIES
    return frozenset()


@dataclass
class APCWifiDevice:
    cooker_id: str
    type: str
    paired_at: str
    name: str
    update_listener: Callable[[APCUpdate], None] | None = None
    # Injected by AnovaWebsocketHandler when the device is discovered, mirroring
    # update_listener: a callback rather than a back-reference to the handler,
    # to avoid a circular import between this module and websocket_handler.py.
    send_command: (
        Callable[[AnovaCommand, dict[str, Any]], Coroutine[Any, Any, None]] | None
    ) = field(default=None, repr=False, compare=False)
    # Cached from the last EVENT_APC_STATE push, regardless of update_listener,
    # so update_running_cook can tell whether a cook is actually active. The
    # device protocol has no persistent job/session id to validate against -
    # job.id in EVENT_APC_STATE is just an echo of the last command's requestId.
    last_update: "APCUpdate | None" = field(default=None, repr=False, compare=False)
    # Wall-clock time the last EVENT_APC_STATE push was received, set by
    # AnovaWebsocketHandler.on_message. Anova's protocol has no offline/disconnect
    # signal (confirmed against the developer docs and by observing a real device
    # unplug - no EVENT_APC_WIFI_REMOVED, no other message, ever arrives), so
    # callers must infer a dead device from silence using this timestamp - the
    # same approach the official Anova app uses.
    last_update_received_at: datetime | None = field(
        default=None, repr=False, compare=False
    )

    def set_update_listener(self, update_function: Callable[[APCUpdate], None]) -> None:
        self.update_listener = update_function

    @property
    def is_cooking(self) -> bool:
        """Whether a cook is currently active, from the last EVENT_APC_STATE push."""
        return self.last_update is not None and self.last_update.binary_sensor.cooking

    @property
    def supported_capabilities(self) -> frozenset[Capability]:
        """The commands this device type supports, regardless of its current state."""
        return get_supported_capabilities(self.type)

    @property
    def available_commands(self) -> frozenset[Capability]:
        """Commands that are valid to call right now: supported by this device
        type AND valid given its current cooking state.

        Reflects last_update, so it's only as fresh as the last state push -
        useful for callers (e.g. deciding which HA entities/services to
        expose) but not a substitute for handling NoActiveCookError, since
        state can change between checking this and calling a command.
        """
        if self.is_cooking:
            valid_now = frozenset(
                {Capability.STOP_COOK, Capability.UPDATE_RUNNING_COOK}
            )
        else:
            valid_now = frozenset({Capability.START_COOK})
        return self.supported_capabilities & valid_now

    def _require_send_command(
        self,
    ) -> Callable[[AnovaCommand, dict[str, Any]], Coroutine[Any, Any, None]]:
        if self.send_command is None:
            raise WebsocketFailure(
                "This device is not attached to an active websocket connection."
            )
        return self.send_command

    def _require_active_cook(self) -> None:
        if not self.is_cooking:
            raise NoActiveCookError(
                "No cook is currently running on this device - target temperature "
                "and timer can only be changed while a cook is active. Use "
                "start_cook to begin one."
            )

    async def update_running_cook(
        self,
        *,
        target_temperature: float | None = None,
        temperature_unit: str | None = None,
        cook_time_seconds: int | None = None,
    ) -> None:
        """Change the target temperature and/or timer of the currently running cook.

        Raises NoActiveCookError if no cook is currently running - see
        build_set_target_temperature_payload for why that can't be validated
        via the device's own RESPONSE instead.
        """
        if target_temperature is None and cook_time_seconds is None:
            raise ValueError(
                "At least one of target_temperature or cook_time_seconds must be given."
            )
        if target_temperature is not None and temperature_unit is None:
            raise ValueError(
                "temperature_unit is required when target_temperature is given."
            )
        self._require_active_cook()

        send_command = self._require_send_command()
        if target_temperature is not None:
            assert temperature_unit is not None
            await send_command(
                AnovaCommand.CMD_APC_SET_TARGET_TEMP,
                build_set_target_temperature_payload(
                    self.cooker_id, self.type, target_temperature, temperature_unit
                ),
            )
        if cook_time_seconds is not None:
            await send_command(
                AnovaCommand.CMD_APC_SET_TIMER,
                build_set_timer_payload(self.cooker_id, self.type, cook_time_seconds),
            )

    async def start_cook(
        self,
        target_temperature: float,
        cook_time_seconds: int,
        temperature_unit: str,
    ) -> None:
        """Start a cook with the given target temperature and timer."""
        await self._require_send_command()(
            AnovaCommand.CMD_APC_START,
            build_start_cook_payload(
                self.cooker_id,
                self.type,
                target_temperature,
                cook_time_seconds,
                temperature_unit,
            ),
        )

    async def stop_cook(self) -> None:
        """Stop the current cook."""
        await self._require_send_command()(
            AnovaCommand.CMD_APC_STOP,
            build_stop_cook_payload(self.cooker_id, self.type),
        )
