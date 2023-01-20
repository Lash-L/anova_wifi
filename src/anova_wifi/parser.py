import logging
from typing import Any

import aiohttp
from sensor_state_data.enum import StrEnum

from anova_wifi.exceptions import AnovaOffline

_LOGGER = logging.getLogger(__name__)


class AnovaPrecisionCookerSensor(StrEnum):
    COOK_TIME = "cook_time"
    MODE = "mode"
    STATE = "state"
    TARGET_TEMPERATURE = "target_temperature"
    COOK_TIME_REMAINING = "cook_time_remaining"
    FIRMWARE_VERSION = "firmware_version"
    HEATER_TEMPERATURE = "heater_temperature"
    TRIAC_TEMPERATURE = "triac_temperature"
    WATER_TEMPERATURE = "water_temperature"


class AnovaPrecisionCookerBinarySensor(StrEnum):
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
    def __init__(self) -> None:
        super().__init__()

    async def update(self, device_key: str) -> dict[str, dict[str, Any]]:
        try:
            async with aiohttp.ClientSession() as session:
                http_response = await session.get(
                    f"https://anovaculinary.io/devices/{device_key}/states/?limit=1"
                )
                anova_status_json = await http_response.json()
            anova_status = anova_status_json[0].get("body")
        except (IndexError, aiohttp.ClientConnectorError):
            raise AnovaOffline()
        return {
            "sensors": {
                AnovaPrecisionCookerSensor.COOK_TIME: anova_status["job"][
                    "cook-time-seconds"
                ],
                AnovaPrecisionCookerSensor.MODE: MODE_MAP.get(
                    anova_status["job"]["mode"], anova_status["job"]["mode"]
                ),
                AnovaPrecisionCookerSensor.STATE: STATE_MAP.get(
                    anova_status["job-status"]["state"],
                    anova_status["job-status"]["state"],
                ),
                AnovaPrecisionCookerSensor.TARGET_TEMPERATURE: anova_status["job"][
                    "target-temperature"
                ],
                AnovaPrecisionCookerSensor.COOK_TIME_REMAINING: anova_status[
                    "job-status"
                ]["cook-time-remaining"],
                AnovaPrecisionCookerSensor.FIRMWARE_VERSION: anova_status[
                    "system-info"
                ]["firmware-version"],
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

    @staticmethod
    def discover() -> None:
        pass
