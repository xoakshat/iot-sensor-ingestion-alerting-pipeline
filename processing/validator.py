
import json
import math
from datetime import datetime, timezone

# Permitted measurement ranges
VALID_RANGES = {
    "temperature": (-40, 100),
    "humidity": (0, 100),
    "air_quality": (0, 500),
}

# Fields required in every sensor message
REQUIRED_FIELDS = ["sensor_id", "type", "value", "unit"]


# Convert input into a usable number
def to_number(raw):

    if isinstance(raw, bool):
        return None

    if isinstance(raw, (int, float)):
        number = float(raw)

    elif isinstance(raw, str):
        try:
            number = float(raw.strip())
        except ValueError:
            return None

    else:
        return None

    return number if math.isfinite(number) else None


# Validate and clean incoming sensor data
def validate(payload):

    try:
        data = json.loads(payload.decode("utf-8"))

    except (UnicodeDecodeError, json.JSONDecodeError):
        return None, "not valid JSON"

    if not isinstance(data, dict):
        return None, "JSON is not an object"

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            return None, f"missing field: {field}"

    # Validate sensor ID
    sensor_id = str(data["sensor_id"]).strip()

    if not sensor_id:
        return None, "empty sensor_id"

    # Validate sensor type
    if data["type"] not in VALID_RANGES:
        return None, f"unknown sensor type: {data['type']}"

    # Convert value into a number
    value = to_number(data["value"])

    if value is None:
        return None, f"value is not a usable number: {data['value']}"

    # Check measurement range
    low, high = VALID_RANGES[data["type"]]

    if not (low <= value <= high):
        return None, f"value {value} outside valid range {low} to {high}"

    # Create clean record
    clean = {
        "sensor_id": sensor_id,
        "type": data["type"],
        "value": round(value, 1),
        "unit": data["unit"],
        "timestamp": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }

    return clean, None
