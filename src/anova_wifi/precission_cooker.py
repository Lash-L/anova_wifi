import secrets
import string
from enum import Enum
from typing import Any

import aiohttp

from anova_wifi.exceptions import AnovaException, AnovaOffline


class AnovaPrecisionCookerSensor(Enum):
    COOK_TIME = "cook_time"
    MODE = "mode"
    STATE = "state"
    TARGET_TEMPERATURE = "target_temperature"
    COOK_TIME_REMAINING = "cook_time_remaining"
    FIRMWARE_VERSION = "firmware_version"
    HEATER_TEMPERATURE = "heater_temperature"
    TRIAC_TEMPERATURE = "triac_temperature"
    WATER_TEMPERATURE = "water_temperature"


class AnovaPrecisionCookerBinarySensor(Enum):
    COOKING = "cooking"
    DEVICE_SAFE = "device_safe"
    WATER_LEAK = "water_leak"
    WATER_LEVEL_CRITICAL = "water_level_critical"
    WATER_TEMP_TOO_HIGH = "water_temp_too_high"


MODE_MAP = {"IDLE": "Idle", "COOK": "Cook", "LOW WATER": "Low water"}

STATE_MAP = {
    "PREHEATING": "Preheating",
    "COOKING": "Cooking",
    "MAINTAINING": "Maintaining",
    "": "No state",
}


class AnovaPrecisionCooker:
    def __init__(
        self, session: aiohttp.ClientSession, device_key: str, type: str, jwt: str
    ) -> None:
        self.session = session
        self.device_key = device_key
        self.type = type
        self._jwt = jwt
        self.cook_time: float | None = None
        self.mode: str | None = None
        self.target_temperature: float | None = None
        self.temperature_unit: float | None = None

    async def update(
        self,
    ) -> dict[
        str, dict[AnovaPrecisionCookerSensor | AnovaPrecisionCookerBinarySensor, Any]
    ]:
        """Updates the Sous vide's data with a non-authenticated api call"""
        try:
            http_response = await self.session.get(
                f"https://anovaculinary.io/devices/{self.device_key}/states/?limit=1"
            )
            anova_status_json = await http_response.json()
            anova_status = anova_status_json[0].get("body")
        except (IndexError, aiohttp.ClientConnectorError):
            raise AnovaOffline()
        system_info = "system-info"
        for key in anova_status.keys():
            if "system-info" in key and "details" not in key and "nxp" not in key:
                system_info = key
                break
        self.mode = anova_status["job"]["mode"]
        self.cook_time = anova_status["job"]["cook-time-seconds"]
        self.target_temperature = anova_status["job"]["target-temperature"]
        self.temperature_unit = anova_status["job"]["temperature-unit"]
        return {
            "sensors": {
                AnovaPrecisionCookerSensor.COOK_TIME: anova_status["job"][
                    "cook-time-seconds"
                ],
                AnovaPrecisionCookerSensor.MODE: MODE_MAP.get(
                    anova_status["job"]["mode"]
                ),
                AnovaPrecisionCookerSensor.STATE: STATE_MAP.get(
                    anova_status["job-status"]["state"],
                ),
                AnovaPrecisionCookerSensor.TARGET_TEMPERATURE: anova_status["job"][
                    "target-temperature"
                ],
                AnovaPrecisionCookerSensor.COOK_TIME_REMAINING: anova_status[
                    "job-status"
                ]["cook-time-remaining"],
                AnovaPrecisionCookerSensor.FIRMWARE_VERSION: anova_status[system_info][
                    "firmware-version"
                ],
                AnovaPrecisionCookerSensor.HEATER_TEMPERATURE: anova_status[
                    "temperature-info"
                ]["heater-temperature"],
                AnovaPrecisionCookerSensor.TRIAC_TEMPERATURE: anova_status[
                    "temperature-info"
                ]["triac-temperature"],
                AnovaPrecisionCookerSensor.WATER_TEMPERATURE: anova_status[
                    "temperature-info"
                ]["water-temperature"],
            },
            "binary_sensors": {
                AnovaPrecisionCookerBinarySensor.COOKING: anova_status["job"]["mode"]
                == "COOK",
                AnovaPrecisionCookerBinarySensor.DEVICE_SAFE: anova_status["pin-info"][
                    "device-safe"
                ]
                == 1,
                AnovaPrecisionCookerBinarySensor.WATER_LEAK: anova_status["pin-info"][
                    "water-leak"
                ]
                == 1,
                AnovaPrecisionCookerBinarySensor.WATER_LEVEL_CRITICAL: anova_status[
                    "pin-info"
                ]["water-level-critical"]
                == 1,
                AnovaPrecisionCookerBinarySensor.WATER_TEMP_TOO_HIGH: anova_status[
                    "pin-info"
                ]["water-temp-too-high"]
                == 1,
            },
        }

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
        json_req = {
            "cook-time-seconds": cook_time if cook_time is not None else self.cook_time,
            "id": "".join(
                secrets.choice(string.ascii_lowercase + string.digits)
                for _ in range(22)
            ),
            # 22 digit random job ID for a new job at every save
            "mode": mode if mode is not None else self.mode,
            "ota-url": "",
            "target-temperature": target_temperature
            if target_temperature is not None
            else self.target_temperature,
            "temperature-unit": temperature_unit
            if temperature_unit is not None
            else self.temperature_unit,
        }
        anova_req_headers = {"authorization": "Bearer " + self._jwt}
        resp = await self.session.put(
            f"https://anovaculinary.io/devices/{self.device_key}/current-job",
            json=json_req,
            headers=anova_req_headers,
        )
        if not resp.ok:
            raise Exception(f"{await resp.text()}")

    async def set_cook_time(self, seconds: int) -> None:
        """Sets how long you want the cook to be"""
        await self.build_request(cook_time=seconds)

    async def set_mode(self, mode: str) -> None:
        """Sets the cooker mode"""
        await self.build_request(mode=mode)

    async def set_target_temperature(self, temperature: float) -> None:
        """Sets the temperature of the cook"""
        await self.build_request(target_temperature=temperature)

    async def set_temperature_unit(self, temperature_unit: str) -> None:
        """Sets the temperature unit for the anova"""
        await self.build_request(temperature_unit=temperature_unit)
