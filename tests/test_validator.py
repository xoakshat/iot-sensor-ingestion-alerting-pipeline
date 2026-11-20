
import json

from processing.validator import validate


def make_payload(data):
    return json.dumps(data).encode("utf-8")


def test_valid_temperature():
    payload = make_payload({
        "sensor_id": "T-01",
        "type": "temperature",
        "value": 28.5,
        "unit": "C"
    })

    clean, reason = validate(payload)

    assert reason is None
    assert clean["sensor_id"] == "T-01"
    assert clean["value"] == 28.5


def test_invalid_json():
    clean, reason = validate(b"not json")

    assert clean is None
    assert reason == "not valid JSON"


def test_missing_field():
    payload = make_payload({
        "sensor_id": "T-01",
        "type": "temperature",
        "value": 28.5
    })

    clean, reason = validate(payload)

    assert clean is None
    assert "missing field" in reason


def test_temperature_out_of_range():
    payload = make_payload({
        "sensor_id": "T-01",
        "type": "temperature",
        "value": 150,
        "unit": "C"
    })

    clean, reason = validate(payload)

    assert clean is None
    assert "outside valid range" in reason


def test_non_numeric_value():
    payload = make_payload({
        "sensor_id": "T-01",
        "type": "temperature",
        "value": "abc",
        "unit": "C"
    })

    clean, reason = validate(payload)

    assert clean is None
    assert "not a usable number" in reason
