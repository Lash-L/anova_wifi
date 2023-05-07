import logging
import secrets
import string
import time
from dataclasses import dataclass

import aiohttp

from anova_wifi.exceptions import AnovaException, AnovaOffline

_LOGGER = logging.getLogger(__name__)


MODE_MAP = {"IDLE": "Idle", "COOK": "Cook", "LOW WATER": "Low water"}

STATE_MAP = {
    "PREHEATING": "Preheating",
    "COOKING": "Cooking",
    "MAINTAINING": "Maintaining",
    "": "No state",
}


@dataclass
class APCUpdateBinary:
    cooking: bool
    preheating: bool
    maintaining: bool
    device_safe: bool
    water_leak: bool
    water_level_critical: bool
    water_temp_too_high: bool


@dataclass
class APCUpdateSensor:
    cook_time: int
    mode: str
    state: str
    target_temperature: float
    cook_time_remaining: int
    firmware_version: str
    heater_temperature: float
    triac_temperature: float
    water_temperature: float


@dataclass
class APCUpdate:
    binary_sensor: APCUpdateBinary
    sensor: APCUpdateSensor


class AnovaPrecisionCooker:
    def __init__(
        self, session: aiohttp.ClientSession, device_key: str, type: str, jwt: str
    ) -> None:
        self.session = session
        self.device_key = device_key
        self.type = type
        self._jwt = jwt
        self.status: APCUpdate | None = None
        self.temperature_unit: str = "C"
        self.last_update: float = 0

    async def update(
        self,
    ) -> APCUpdate:
        """Updates the Sous vide's data with a non-authenticated api call"""
        if time.monotonic() - self.last_update < 15 and self.status is not None:
            return self.status
        try:
            http_response = await self.session.get(
                f"https://anovaculinary.io/devices/{self.device_key}/states/?limit=1"
            )
            anova_status_json = await http_response.json()
            anova_status = anova_status_json[0].get("body")
            _LOGGER.debug("Got status: %s", anova_status)
        except (IndexError, aiohttp.ClientConnectorError):
            raise AnovaOffline(
                "Cannot connect to sous vide - perhaps it is not online?"
            )
        system_info = "system-info"
        for key in anova_status.keys():
            if "system-info" in key and "details" not in key and "nxp" not in key:
                system_info = key
                break
        binary_sensor = APCUpdateBinary(
            cooking=anova_status["job-status"]["state"] == "COOKING",
            preheating=anova_status["job-status"]["state"] == "PREHEATING",
            maintaining=anova_status["job-status"]["state"] == "MAINTAINING",
            device_safe=anova_status["pin-info"]["device-safe"] == 1,
            water_leak=anova_status["pin-info"]["water-leak"] == 1,
            water_level_critical=anova_status["pin-info"]["water-level-critical"] == 1,
            water_temp_too_high=anova_status["pin-info"]["water-temp-too-high"] == 1
            if "water-temp-too-high" in anova_status["pin-info"]
            else None,
        )
        sensor = APCUpdateSensor(
            cook_time=anova_status["job"]["cook-time-seconds"],
            mode=MODE_MAP.get(anova_status["job"]["mode"], "Unknown"),
            state=STATE_MAP.get(anova_status["job-status"]["state"], "No state"),
            target_temperature=anova_status["job"]["target-temperature"],
            cook_time_remaining=anova_status["job-status"]["cook-time-remaining"],
            firmware_version=anova_status[system_info]["firmware-version"],
            heater_temperature=anova_status["temperature-info"]["heater-temperature"],
            triac_temperature=anova_status["temperature-info"]["triac-temperature"],
            water_temperature=anova_status["temperature-info"]["water-temperature"],
        )
        self.status = APCUpdate(
            binary_sensor=binary_sensor,
            sensor=sensor,
        )
        return self.status

    async def build_request(
        self,
        cook_time: int | None = None,
        mode: str | None = None,
        target_temperature: float | None = None,
        temperature_unit: str | None = None,
    ) -> None:
        """Builds an api call for the sous vide"""
        if self._jwt is None:
            raise AnovaException("No JWT - ")
        if self.status is None:
            raise AnovaException("No status - cannot build request")
        json_req = {
            "cook-time-seconds": cook_time
            if cook_time is not None
            else self.status.sensor.cook_time,
            "id": "".join(
                secrets.choice(string.ascii_lowercase + string.digits)
                for _ in range(22)
            ),
            # 22 digit random job ID for a new job at every save
            "mode": mode if mode is not None else self.status.sensor.mode,
            "ota-url": "",
            "target-temperature": target_temperature
            if target_temperature is not None
            else self.status.sensor.target_temperature,
            "temperature-unit": temperature_unit
            if temperature_unit is not None
            else self.temperature_unit,
        }
        anova_req_headers = {"authorization": "Bearer " + self._jwt}
        _LOGGER.debug(
            "Sending https://anovaculinary.io/devices/%s/current-job with json %s and headers %s",
            self.device_key,
            json_req,
            anova_req_headers,
        )
        resp = await self.session.put(
            f"https://anovaculinary.io/devices/{self.device_key}/current-job",
            json=json_req,
            headers=anova_req_headers,
        )
        if not resp.ok:
            raise AnovaException(f"{await resp.text()}")
        else:
            sous_vide_state = await resp.json()
            _LOGGER.debug("Got response %s", sous_vide_state)
            self.status.sensor.cook_time = sous_vide_state["cook-time-seconds"]
            self.status.sensor.mode = sous_vide_state["mode"]
            self.status.sensor.target_temperature = sous_vide_state[
                "target-temperature"
            ]
            self.temperature_unit = sous_vide_state["temperature-unit"]
            self.last_update = time.monotonic()

    async def set_cook_time(self, seconds: int) -> None:
        """Sets how long you want the cook to be"""
        await self.build_request(cook_time=seconds)

    async def set_mode(self, mode: str) -> None:
        """Sets the cooker mode"""
        await self.build_request(mode=mode)

    async def set_target_temperature(self, temperature: float) -> None:
        """Sets the temperature of the cook"""
        temp = round(temperature, 2)
        await self.build_request(target_temperature=temp)

    async def set_temperature_unit(self, temperature_unit: str) -> None:
        """Sets the temperature unit for the anova"""
        await self.build_request(temperature_unit=temperature_unit)
