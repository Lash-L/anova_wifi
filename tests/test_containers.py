from copy import deepcopy

from anova_wifi.web_socket_containers import (
    AnovaA3State,
    AnovaState,
    build_a3_payload,
    build_a6_a7_payload,
    build_wifi_cooker_state_body,
)
from tests.example_data import (
    A3_MESSAGE,
    A4_MESSAGE,
    A6_MESSAGE,
    A7_COOKING,
    A7_MESSAGE,
)


def test_a3_payload():
    resp = build_a3_payload(A3_MESSAGE["payload"]["state"])
    # Ensure some of the basics
    assert resp.sensor.target_temperature == 96.1
    assert resp.sensor.a3_state == AnovaA3State.cooking.name
    assert resp.sensor.cook_time_remaining == 840


def test_a4_payload():
    resp = build_wifi_cooker_state_body(A4_MESSAGE["payload"]["state"]).to_apc_update()
    # Ensure some of the basics
    assert resp.sensor.target_temperature == 66.11
    assert resp.sensor.state == AnovaState.cooking.name
    assert resp.sensor.cook_time_remaining == 0


def test_a7_payload():
    resp = build_a6_a7_payload(A7_MESSAGE["payload"]["state"])
    assert resp.sensor.mode == "idle"
    assert resp.sensor.state == AnovaState.no_state.name
    assert resp.sensor.cook_time == 36000
    assert resp.sensor.cook_time_remaining == 0
    assert resp.binary_sensor.cooking is False
    assert resp.binary_sensor.preheating is False
    assert resp.binary_sensor.maintaining is False


def test_a7_cooking():
    resp = build_a6_a7_payload(A7_COOKING["payload"]["state"])
    assert resp.sensor.mode == "cook"
    assert resp.sensor.state == AnovaState.cooking.name
    assert resp.sensor.cook_time == 1200
    assert resp.sensor.cook_time_remaining == 1154
    assert resp.binary_sensor.cooking is True
    assert resp.binary_sensor.preheating is False
    assert resp.binary_sensor.maintaining is False


def test_a7_preheating():
    message = deepcopy(A7_COOKING)
    state = message["payload"]["state"]
    state["nodes"]["timer"]["mode"] = "running"
    state["cook"]["activeStageMode"] = "entering"

    resp = build_a6_a7_payload(state)
    assert resp.sensor.mode == "cook"
    assert resp.sensor.state == AnovaState.preheating.name
    assert resp.sensor.cook_time == 1200
    assert resp.sensor.cook_time_remaining == 1200
    assert resp.binary_sensor.cooking is True
    assert resp.binary_sensor.preheating is True
    assert resp.binary_sensor.maintaining is False


def test_a7_timer_expired():
    message = deepcopy(A7_COOKING)
    state = message["payload"]["state"]
    state["nodes"]["timer"]["mode"] = "completed"
    state["cook"]["activeStageMode"] = "running"

    resp = build_a6_a7_payload(state)
    assert resp.sensor.mode == "cook"
    assert resp.sensor.state == AnovaState.timer_expired.name
    assert resp.sensor.cook_time == 1200
    assert resp.sensor.cook_time_remaining == 0
    assert resp.binary_sensor.cooking is True
    assert resp.binary_sensor.preheating is False
    assert resp.binary_sensor.maintaining is True


def test_a7_cooking_without_timestamps():
    message = deepcopy(A7_COOKING)
    state = message["payload"]["state"]
    state["nodes"]["timer"].pop("startedAtTimestamp")
    state.pop("updatedTimestamp")

    resp = build_a6_a7_payload(state)
    assert resp.sensor.mode == "cook"
    assert resp.sensor.state == AnovaState.cooking.name
    assert resp.sensor.cook_time == 1200
    assert resp.sensor.cook_time_remaining == 1200
    assert resp.binary_sensor.cooking is True
    assert resp.binary_sensor.preheating is False
    assert resp.binary_sensor.maintaining is False


def test_a6_payload():
    resp = build_a6_a7_payload(A6_MESSAGE["payload"]["state"])
    assert resp.sensor.mode == "idle"
    assert resp.sensor.cook_time == 7200
    assert resp.sensor.target_temperature == 57.2
