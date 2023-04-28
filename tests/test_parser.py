from unittest import mock

import aiohttp
import pytest

from anova_wifi import AnovaOffline
from anova_wifi.precission_cooker import AnovaPrecisionCooker

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


@pytest.mark.asyncio
async def test_can_create():
    async with aiohttp.ClientSession() as session:
        AnovaPrecisionCooker(session, "", "", "")


@pytest.mark.asyncio
@mock.patch("anova_wifi.parser.aiohttp.ClientResponse.json")
async def test_async_data_1(json_mocked):
    async with aiohttp.ClientSession() as session:
        apc = AnovaPrecisionCooker(session, "", "", "")
        json_mocked.return_value = dataset_one
        result = await apc.update()
        sensors = result.sensor
        assert sensors.cook_time == 0
        assert sensors.mode == "Idle"
        assert sensors.state == "No state"
        assert sensors.target_temperature == 54.72
        assert sensors.cook_time_remaining == 0
        assert sensors.firmware_version == "2.2.0"
        assert sensors.heater_temperature == 22.37
        assert sensors.triac_temperature == 36.04
        assert sensors.water_temperature == 18.33
        binary_sensors = result.binary_sensor
        assert not binary_sensors.cooking
        assert not binary_sensors.preheating
        assert not binary_sensors.maintaining
        assert not binary_sensors.device_safe
        assert not binary_sensors.water_leak
        assert not binary_sensors.water_level_critical
        assert not binary_sensors.water_temp_too_high


@pytest.mark.asyncio
async def test_async_no_return():
    async with aiohttp.ClientSession() as session:
        apc = AnovaPrecisionCooker(session, "", "", "")
        with pytest.raises(AnovaOffline):
            await apc.update()
