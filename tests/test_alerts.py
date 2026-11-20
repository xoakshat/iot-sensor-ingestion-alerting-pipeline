
import pytest

from alerts import engine


@pytest.fixture(autouse=True)
def reset_alarm_state():
    engine.in_alarm.clear()


def make_reading(value):
    return {
        "sensor_id": "T-01",
        "type": "temperature",
        "value": value,
        "unit": "C",
        "timestamp": "2026-11-20T10:00:00+00:00"
    }


def test_normal_temperature_no_alert():
    alerts = engine.check_reading(make_reading(28.0))

    assert alerts == []


def test_high_temperature_generates_alert():
    alerts = engine.check_reading(make_reading(47.8))

    assert len(alerts) == 1
    assert alerts[0]["sensor_id"] == "T-01"
    assert alerts[0]["value"] == 47.8
    assert alerts[0]["threshold"] == "> 40"


def test_repeated_high_temperature_no_duplicate():
    engine.check_reading(make_reading(47.8))

    alerts = engine.check_reading(make_reading(49.2))

    assert alerts == []


def test_recovery_allows_new_alert():
    engine.check_reading(make_reading(47.8))

    # Temperature returns to normal
    engine.check_reading(make_reading(28.0))

    # Temperature becomes high again
    alerts = engine.check_reading(make_reading(47.5))

    assert len(alerts) == 1
    assert alerts[0]["value"] == 47.5
