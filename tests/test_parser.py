from unittest import mock

import pytest

from anova_wifi import AnovaOffline
from anova_wifi.parser import (
    AnovaPrecisionCooker,
    AnovaPrecisionCookerBinarySensor,
    AnovaPrecisionCookerSensor,
)

dataset_one = [
    {
        "body": {
            "boot-id": "8620610049456548422",
            "job": {
                "cook-time-seconds": 0,
                "id": "8759286e3125b0c547",
                "mode": "IDLE",
                "ota-url": "",
                "target-temperature": 54.72,
                "temperature-unit": "F",
            },
            "job-status": {
                "cook-time-remaining": 0,
                "job-start-systick": 599679,
                "provisioning-pairing-code": 7514,
                "state": "",
                "state-change-systick": 599679,
            },
            "pin-info": {
                "device-safe": 0,
                "water-leak": 0,
                "water-level-critical": 0,
                "water-temp-too-high": 0,
            },
            "system-info": {
                "class": "A5",
                "firmware-version": "2.2.0",
                "type": "RA2L1-128",
            },
            "system-info-details": {
                "firmware-version-raw": "VM178_A_02.02.00_MKE15-128",
                "systick": 607026,
                "version-string": "VM171_A_02.02.00 RA2L1-128",
            },
            "temperature-info": {
                "heater-temperature": 22.37,
                "triac-temperature": 36.04,
                "water-temperature": 18.33,
            },
        },
        "header": {
            "created-at": "2023-01-18T18:31:31.935167Z",
            "e-tag": "bc774980b466691bae55bcc715f20ab6414009a2c21d40d2ba946c5e5a5e5692",
            "entity-id": "8018572930165770228",
        },
    }
]


def test_can_create():
    AnovaPrecisionCooker()


@pytest.mark.asyncio
@mock.patch("anova_wifi.parser.aiohttp.ClientResponse.json")
async def test_async_data_1(json_mocked):
    apc = AnovaPrecisionCooker()
    json_mocked.return_value = dataset_one
    result = await apc.update("")
    assert result == {
        "sensors": {
            AnovaPrecisionCookerSensor.COOK_TIME: 0,
            AnovaPrecisionCookerSensor.MODE: "Idle",
            AnovaPrecisionCookerSensor.STATE: "No state",
            AnovaPrecisionCookerSensor.TARGET_TEMPERATURE: 54.72,
            AnovaPrecisionCookerSensor.COOK_TIME_REMAINING: 0,
            AnovaPrecisionCookerSensor.FIRMWARE_VERSION: "2.2.0",
            AnovaPrecisionCookerSensor.HEATER_TEMPERATURE: 22.37,
            AnovaPrecisionCookerSensor.TRIAC_TEMPERATURE: 36.04,
            AnovaPrecisionCookerSensor.WATER_TEMPERATURE: 18.33,
        },
        "binary_sensors": {
            AnovaPrecisionCookerBinarySensor.COOKING: False,
            AnovaPrecisionCookerBinarySensor.DEVICE_SAFE: False,
            AnovaPrecisionCookerBinarySensor.WATER_LEAK: False,
            AnovaPrecisionCookerBinarySensor.WATER_LEVEL_CRITICAL: False,
            AnovaPrecisionCookerBinarySensor.WATER_TEMP_TOO_HIGH: False,
        },
    }


@pytest.mark.asyncio
async def test_async_no_return():
    apc = AnovaPrecisionCooker()
    with pytest.raises(AnovaOffline):
        await apc.update("f")

