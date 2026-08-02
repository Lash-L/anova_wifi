import pytest

from anova_wifi import (
    APCUpdate,
    APCUpdateBinary,
    APCUpdateSensor,
    APCWifiDevice,
    Capability,
    get_supported_capabilities,
)


@pytest.mark.parametrize(
    "device_type", ["a3", "a4", "a5", "a6", "a7", "a8", "pro"], ids=str
)
def test_apc_types_support_all_commands(device_type: str) -> None:
    assert get_supported_capabilities(device_type) == frozenset(Capability)


@pytest.mark.parametrize("device_type", ["oven_v1", "oven_v2", "unknown", ""], ids=str)
def test_non_apc_types_support_no_commands(device_type: str) -> None:
    assert get_supported_capabilities(device_type) == frozenset()


def test_device_supported_capabilities_property() -> None:
    device = APCWifiDevice(cooker_id="x", type="pro", paired_at="now", name="test")
    assert device.supported_capabilities == frozenset(Capability)


def test_device_supported_capabilities_property_unknown_type() -> None:
    device = APCWifiDevice(cooker_id="x", type="oven_v1", paired_at="now", name="test")
    assert device.supported_capabilities == frozenset()


def test_available_commands_idle() -> None:
    device = APCWifiDevice(cooker_id="x", type="pro", paired_at="now", name="test")
    assert device.available_commands == frozenset({Capability.START_COOK})


def test_available_commands_unknown_type_is_always_empty() -> None:
    device = APCWifiDevice(cooker_id="x", type="oven_v1", paired_at="now", name="test")
    assert device.available_commands == frozenset()


def test_available_commands_while_cooking() -> None:
    device = APCWifiDevice(cooker_id="x", type="pro", paired_at="now", name="test")
    device.last_update = APCUpdate(
        binary_sensor=APCUpdateBinary(cooking=True),
        sensor=APCUpdateSensor(mode="cook"),
    )

    assert device.available_commands == frozenset(
        {Capability.STOP_COOK, Capability.UPDATE_RUNNING_COOK}
    )


def test_available_commands_while_cooking_unknown_type_is_always_empty() -> None:
    device = APCWifiDevice(cooker_id="x", type="oven_v1", paired_at="now", name="test")
    device.last_update = APCUpdate(
        binary_sensor=APCUpdateBinary(cooking=True),
        sensor=APCUpdateSensor(mode="cook"),
    )

    assert device.available_commands == frozenset()
