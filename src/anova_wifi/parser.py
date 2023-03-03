import datetime
import logging
from typing import Any

import aiohttp
from aiohttp import ClientWebSocketResponse
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


SOUS_VIDE_MODE_MAP = {"IDLE": "Idle", "COOK": "Cook", "LOW WATER": "Low water"}

SOUS_VIDE_STATE_MAP = {
    "PREHEATING": "Preheating",
    "COOKING": "Cooking",
    "MAINTAINING": "Maintaining",
    "": "No state",
}


class AnovaPrecisionCooker:
    def __init__(self, session: aiohttp.ClientSession) -> None:
        self.session = session

    async def update(self, device_key: str) -> dict[str, dict[str, Any]]:
        try:
            http_response = await self.session.get(
                f"https://anovaculinary.io/devices/{device_key}/states/?limit=1"
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
        return {
            "sensors": {
                AnovaPrecisionCookerSensor.COOK_TIME: anova_status["job"][
                    "cook-time-seconds"
                ],
                AnovaPrecisionCookerSensor.MODE: SOUS_VIDE_MODE_MAP.get(
                    anova_status["job"]["mode"], anova_status["job"]["mode"]
                ),
                AnovaPrecisionCookerSensor.STATE: SOUS_VIDE_STATE_MAP.get(
                    anova_status["job-status"]["state"],
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

    @staticmethod
    def discover() -> None:
        pass

class AnovaPrecisionOvenSensor(StrEnum):
    COOKER_ID = "cooker_id"
    STAGE_TYPE = "stage_type"
    FAN_SPEED = "fan_speed"
    RACK_POSITION = "rack_position"
    STAGE_MODE = "stage_mode"
    STAGE_TEMPERATURE = "stage_temperature"
    STEAM_GENERATOR_MODE = "steam_generator_mode"
    STEAM_GENERATOR_HUMIDITY = "steam_generator_humidity"


class AnovaPrecisionOvenBinarySensor(StrEnum):
    VENT = "vent"
    TOP_HEATING = "top_heating"
    BOTTOM_HEATING = "bottom_heating"
    REAR_HEATING = "rear_heating"


class AnovaPrecisionOven:
    def __init__(self, session: aiohttp.ClientSession, username: str, password: str):
        self.session = session
        self.username = username
        self.password = password
        self.authentication_token: str | None = None
        self.authentication_expiration: datetime.datetime = datetime.datetime.now()
        self.websocket_client: ClientWebSocketResponse | None = None

    async def authenticate(self) -> bool:
        """Authenticate with the Anova API"""
        # If auth fails, raise invalid login
        # If some other issue, raise Anova offline
        pass

    async def websocket_connect(self):
        """I don't have much experience with websockets, but I know when you connect with ws_connect
        aiohttp returns ClientWebSocketResponse that can then be used to communicate with the ws.
        If we could just carry that response around that would be ideal, so that we don't have to constantly reconnect
        """
        pass

    async def start_cook(self):
        pass

    async def stop_cook(self):
        pass

    async def parse_oven_state(self):
        pass

