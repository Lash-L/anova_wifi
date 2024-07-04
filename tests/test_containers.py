from anova_wifi.web_socket_containers import (
    AnovaA3State,
    AnovaState,
    build_a3_payload,
    build_wifi_cooker_state_body,
)
from tests.example_data import A3_MESSAGE, A4_MESSAGE


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
