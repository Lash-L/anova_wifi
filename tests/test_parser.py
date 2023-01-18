from unittest import mock

from sensor_state_data import (
    BinarySensorDescription,
    BinarySensorValue,
    DeviceKey,
    SensorDescription,
    SensorDeviceClass,
    SensorDeviceInfo,
    SensorUpdate,
    SensorValue,
    Units,
)

from anova_wifi.parser import AnovaPrecisionCooker
from tests import MockResponse

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


@mock.patch("anova_wifi.parser.requests.get")
def test_data_1(requests_mocked):
    apc = AnovaPrecisionCooker()
    requests_mocked.return_value = MockResponse(json_data=dataset_one, status_code=200)
    result = apc.update("")
    print(result)
    assert result == SensorUpdate(
        title=None,
        devices={
            None: SensorDeviceInfo(
                name=None,
                model=None,
                manufacturer="Anova",
                sw_version=None,
                hw_version=None,
            )
        },
        entity_descriptions={
            DeviceKey(key="target_temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="target_temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_FAHRENHEIT,
            ),
            DeviceKey(key="state", device_id=None): SensorDescription(
                device_key=DeviceKey(key="state", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="cook_time", device_id=None): SensorDescription(
                device_key=DeviceKey(key="cook_time", device_id=None),
                device_class=SensorDeviceClass.DURATION,
                native_unit_of_measurement=Units.TIME_SECONDS,
            ),
            DeviceKey(key="mode", device_id=None): SensorDescription(
                device_key=DeviceKey(key="mode", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="cook_time_remaining", device_id=None): SensorDescription(
                device_key=DeviceKey(key="cook_time_remaining", device_id=None),
                device_class=None,
                native_unit_of_measurement=Units.TIME_SECONDS,
            ),
            DeviceKey(key="firmware_version", device_id=None): SensorDescription(
                device_key=DeviceKey(key="firmware_version", device_id=None),
                device_class=None,
                native_unit_of_measurement=None,
            ),
            DeviceKey(key="heater_temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="heater_temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_FAHRENHEIT,
            ),
            DeviceKey(key="triac_temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="triac_temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_FAHRENHEIT,
            ),
            DeviceKey(key="water_temperature", device_id=None): SensorDescription(
                device_key=DeviceKey(key="water_temperature", device_id=None),
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=Units.TEMP_FAHRENHEIT,
            ),
        },
        entity_values={
            DeviceKey(key="target_temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="target_temperature", device_id=None),
                name="Target Temperature",
                native_value=54.72,
            ),
            DeviceKey(key="state", device_id=None): SensorValue(
                device_key=DeviceKey(key="state", device_id=None),
                name="State",
                native_value="",
            ),
            DeviceKey(key="cook_time", device_id=None): SensorValue(
                device_key=DeviceKey(key="cook_time", device_id=None),
                name="Cook Time",
                native_value=0,
            ),
            DeviceKey(key="mode", device_id=None): SensorValue(
                device_key=DeviceKey(key="mode", device_id=None),
                name="Mode",
                native_value="IDLE",
            ),
            DeviceKey(key="cook_time_remaining", device_id=None): SensorValue(
                device_key=DeviceKey(key="cook_time_remaining", device_id=None),
                name="Cook Time Remaining",
                native_value=0,
            ),
            DeviceKey(key="firmware_version", device_id=None): SensorValue(
                device_key=DeviceKey(key="firmware_version", device_id=None),
                name="Firmware Version",
                native_value="2.2.0",
            ),
            DeviceKey(key="heater_temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="heater_temperature", device_id=None),
                name="Heater Temperature",
                native_value=22.37,
            ),
            DeviceKey(key="triac_temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="triac_temperature", device_id=None),
                name="Triac Temperature",
                native_value=36.04,
            ),
            DeviceKey(key="water_temperature", device_id=None): SensorValue(
                device_key=DeviceKey(key="water_temperature", device_id=None),
                name="Water Temperature",
                native_value=18.33,
            ),
        },
        binary_entity_descriptions={
            DeviceKey(key="cooking", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="cooking", device_id=None), device_class=None
            ),
            DeviceKey(key="device_safe", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="device_safe", device_id=None),
                device_class=None,
            ),
            DeviceKey(key="water_leak", device_id=None): BinarySensorDescription(
                device_key=DeviceKey(key="water_leak", device_id=None),
                device_class=None,
            ),
            DeviceKey(
                key="water_level_critical", device_id=None
            ): BinarySensorDescription(
                device_key=DeviceKey(key="water_level_critical", device_id=None),
                device_class=None,
            ),
            DeviceKey(
                key="water_temp_too_high", device_id=None
            ): BinarySensorDescription(
                device_key=DeviceKey(key="water_temp_too_high", device_id=None),
                device_class=None,
            ),
        },
        binary_entity_values={
            DeviceKey(key="cooking", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="cooking", device_id=None),
                name="Cooking",
                native_value=False,
            ),
            DeviceKey(key="device_safe", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="device_safe", device_id=None),
                name="Device Safe",
                native_value=False,
            ),
            DeviceKey(key="water_leak", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="water_leak", device_id=None),
                name="Water Leak",
                native_value=False,
            ),
            DeviceKey(key="water_level_critical", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="water_level_critical", device_id=None),
                name="Water Level Critical",
                native_value=False,
            ),
            DeviceKey(key="water_temp_too_high", device_id=None): BinarySensorValue(
                device_key=DeviceKey(key="water_temp_too_high", device_id=None),
                name="Water Temperature Too High",
                native_value=False,
            ),
        },
        events={},
    )
