import logging
from typing import Any

import requests
from sensor_state_data import SensorData, SensorDeviceClass, Units
from sensor_state_data.enum import StrEnum

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


TEMP_MAP = {"F": Units.TEMP_FAHRENHEIT, "C": Units.TEMP_CELSIUS}


class AnovaPrecisionCooker(SensorData):
    def __init__(self, device_key: str):
        super().__init__()
        self.device_key = device_key

    def _start_update(self, data: Any) -> None:
        anova_status = (
            requests.get(
                f"https://anovaculinary.io/devices/{self.device_key}/states/?limit=1"
            )
            .json()[0]
            .get("body")
        )
        self.set_device_manufacturer("Anova")
        temp_unit = TEMP_MAP.get(anova_status["job"]["temperature-unit"])
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.COOK_TIME),
            Units.TIME_SECONDS,
            anova_status["job"]["cook-time-seconds"],
            SensorDeviceClass.DURATION,
            "Cook Time",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.MODE),
            None,
            anova_status["job"]["mode"],
            None,
            "Mode",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.STATE),
            None,
            anova_status["job-status"]["state"],
            None,
            "State",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.TARGET_TEMPERATURE),
            temp_unit,
            anova_status["job"]["target-temperature"],
            SensorDeviceClass.TEMPERATURE,
            "Target Temperature",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.COOK_TIME_REMAINING),
            Units.TIME_SECONDS,
            anova_status["job-status"]["cook-time-remaining"],
            None,
            "Cook Time Remaining",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.FIRMWARE_VERSION),
            None,
            anova_status["system-info"]["firmware-version"],
            None,
            "Mode",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.HEATER_TEMPERATURE),
            temp_unit,
            anova_status["temperature-info"]["heater-temperature"],
            SensorDeviceClass.TEMPERATURE,
            "Heater Temperature",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.TRIAC_TEMPERATURE),
            temp_unit,
            anova_status["temperature-info"]["triac-temperature"],
            SensorDeviceClass.TEMPERATURE,
            "Triac Temperature",
        )
        self.update_sensor(
            str(AnovaPrecisionCookerSensor.WATER_TEMPERATURE),
            temp_unit,
            anova_status["temperature-info"]["water-temperature"],
            SensorDeviceClass.TEMPERATURE,
            "Water Temperature",
        )
        self.update_binary_sensor(
            str(AnovaPrecisionCookerBinarySensor.COOKING),
            anova_status["job"]["mode"] == "COOK",
            None,
            "Water Temperature Too High",
        )
        self.update_binary_sensor(
            str(AnovaPrecisionCookerBinarySensor.DEVICE_SAFE),
            anova_status["pin-info"]["device-safe"] == 1,
            None,
            "Device Safe",
        )
        self.update_binary_sensor(
            str(AnovaPrecisionCookerBinarySensor.WATER_LEAK),
            anova_status["pin-info"]["water-leak"] == 1,
            None,
            "Water Leak",
        )
        self.update_binary_sensor(
            str(AnovaPrecisionCookerBinarySensor.WATER_LEVEL_CRITICAL),
            anova_status["pin-info"]["water-level-critical"] == 1,
            None,
            "Water Level Critical",
        )
        self.update_binary_sensor(
            str(AnovaPrecisionCookerBinarySensor.WATER_TEMP_TOO_HIGH),
            anova_status["pin-info"]["water-temp-too-high"] == 1,
            None,
            "Water Temperature Too High",
        )

    @staticmethod
    def discover() -> None:
        pass
