
import json
import time
import paho.mqtt.client as mqtt

SEQUENCE = [
    ("T-01", "temperature", 28.0, "C"),
    ("T-01", "temperature", 47.8, "C"),
    ("T-01", "temperature", 49.2, "C"),
    ("T-01", "temperature", 47.8, "C"),
    ("T-01", "temperature", 28.0, "C"),
    ("T-01", "temperature", 47.5, "C"),
    ("H-01", "humidity", 92.0, "%"),
    ("H-01", "humidity", 50.0, "%"),
    ("H-01", "humidity", 10.0, "%"),
    ("A-01", "air_quality", 210.0, "AQI"),
    ("T-02", "temperature", 47.8, "C"),
]

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.connect("localhost", 1883)

client.loop_start()

for sensor_id, kind, value, unit in SEQUENCE:

    message = {
        "sensor_id": sensor_id,
        "type": kind,
        "value": value,
        "unit": unit
    }

    topic = f"sensors/{kind}/{sensor_id}"

    client.publish(
        topic,
        json.dumps(message)
    ).wait_for_publish()

    print("Sent:", message)

    time.sleep(0.5)

client.loop_stop()
client.disconnect()

print("Spike test completed!")
