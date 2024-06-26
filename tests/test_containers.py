from anova_wifi.web_socket_containers import AnovaA3State, build_a3_payload
from tests.example_data import A3_MESSAGE


def test_a3_payload():
    resp = build_a3_payload(A3_MESSAGE["payload"]["state"])
    # Ensure some of the basics
    assert resp.sensor.target_temperature == 96.1
    assert resp.sensor.a3_state == AnovaA3State.cooking
    assert resp.sensor.cook_time_remaining == 840
