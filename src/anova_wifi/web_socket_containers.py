from dataclasses import dataclass
from enum import Enum
from typing import Any, Callable


@dataclass
class APCUpdateBinary:
    cooking: bool
    preheating: bool
    maintaining: bool
    device_safe: bool | None
    water_leak: bool | None
    water_level_critical: bool | None
    water_temp_too_high: bool | None
    water_level_low: bool | None


@dataclass
class APCUpdateSensor:
    cook_time: int
    mode: str
    state: str
    target_temperature: float
    cook_time_remaining: int | None
    firmware_version: str
    heater_temperature: float | None
    triac_temperature: float | None
    water_temperature: float


@dataclass
class APCUpdate:
    binary_sensor: APCUpdateBinary
    sensor: APCUpdateSensor


class AnovaMode(str, Enum):
    STARTUP = "STARTUP"
    IDLE = "IDLE"
    COOK = "COOK"
    LOW_WATER = "LOW WATER"
    OTA = "OTA"
    PROVISIONING = "PROVISIONING"
    HIGH_TEMP = "HIGH TEMP"
    DEVICE_FAILURE = "DEVICE FAILURE"


class AnovaState(str, Enum):
    PREHEATING = "PREHEATING"
    COOKING = "COOKING"
    MAINTAINING = "MAINTAINING"
    TIMER_EXPIRED = "TIMER EXPIRED"
    SET_TIMER = "SET TIMER"
    NO_STATE = ""


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
    class_name: str | None
    firmware_version: str
    type: str


@dataclass
class WifiSystemInfo3220:
    firmware_version: str
    has_real_cert_catalog: str
    firmware_version_raw: str


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
        sensors = APCUpdateSensor(
            cook_time=self.job.cook_time_seconds,
            mode=self.job.mode,
            state=self.job_status.state,
            target_temperature=self.job.target_temperature,
            cook_time_remaining=self.job_status.cook_time_remaining,
            firmware_version=self.firmware_version,
            heater_temperature=self.temperature_info.heater_temperature,
            triac_temperature=self.temperature_info.triac_temperature,
            water_temperature=self.temperature_info.water_temperature,
        )

        binary_sensors = APCUpdateBinary(
            cooking=bool(self.job.mode == AnovaMode.COOK),
            preheating=bool(self.job_status.state == AnovaState.PREHEATING),
            maintaining=bool(
                self.job_status.state == AnovaState.MAINTAINING
                or self.job_status.state == AnovaState.TIMER_EXPIRED
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
        is_device_safe=bool(pin_info_json["device-safe"])
        if "device-safe" in pin_info_json
        else None,
        is_water_leak=bool(pin_info_json.get("water-leak"))
        if "water-leak" in pin_info_json
        else None,
        is_water_level_critical=bool(pin_info_json.get("water-level-critical"))
        if "water-level-critical" in pin_info_json
        else None,
        is_water_level_low=bool(pin_info_json.get("water-level-low"))
        if "water-level-low" in pin_info_json
        else None,
        water_temp_too_high=bool(pin_info_json.get("water-temp-too-high"))
        if "water-temp-too-high" in pin_info_json
        else None,
    )
    system_info_json: dict[str, str] | None = apc_response.get("system-info")
    if system_info_json is not None:
        system_info = WifiSystemInfo(
            firmware_version=system_info_json["firmware-version"],
            class_name=system_info_json.get("class"),
            type=system_info_json["type"],
        )
    system_info_3220_json: dict[str, str] | None = apc_response.get("system-info-3220")
    if system_info_3220_json:
        system_info_3220 = WifiSystemInfo3220(
            firmware_version=system_info_3220_json["firmware-version"],
            has_real_cert_catalog=system_info_3220_json["has-real-cert-catalog"],
            firmware_version_raw=system_info_3220_json["firmware-version-raw"],
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


@dataclass
class APCWifiDevice:
    cooker_id: str
    type: str
    paired_at: str
    name: str
    update_listener: Callable[[APCUpdate], None] | None = None

    def set_update_listener(self, update_function: Callable[[APCUpdate], None]) -> None:
        self.update_listener = update_function
