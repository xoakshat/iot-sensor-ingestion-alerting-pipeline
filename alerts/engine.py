
RULES = [
    {
        "type": "temperature",
        "op": ">",
        "limit": 40,
        "message": "Temperature exceeded safe limit"
    },
    {
        "type": "humidity",
        "op": ">",
        "limit": 80,
        "message": "Humidity too high"
    },
    {
        "type": "humidity",
        "op": "<",
        "limit": 25,
        "message": "Humidity too low"
    },
    {
        "type": "air_quality",
        "op": ">",
        "limit": 150,
        "message": "Air quality is poor"
    },
]

in_alarm = set()


def violates(value, op, limit):
    if op == ">":
        return value > limit

    if op == "<":
        return value < limit

    return False


def check_reading(reading):
    new_alerts = []

    for number, rule in enumerate(RULES):

        if rule["type"] != reading["type"]:
            continue

        key = (reading["sensor_id"], number)

        if violates(reading["value"], rule["op"], rule["limit"]):

            if key not in in_alarm:
                in_alarm.add(key)

                new_alerts.append({
                    "sensor_id": reading["sensor_id"],
                    "type": reading["type"],
                    "value": reading["value"],
                    "threshold": f"{rule['op']} {rule['limit']}",
                    "message": rule["message"],
                    "timestamp": reading["timestamp"],
                })

        else:
            in_alarm.discard(key)

    return new_alerts
