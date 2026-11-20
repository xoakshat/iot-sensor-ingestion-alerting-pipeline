
import json
import random
import time
import sys
import paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
INTERVAL = 2

# Sensor IDs that should stop sending readings
MUTED = sys.argv[1:]

SENSORS = [
    {"sensor_id": "T-01", "type": "temperature", "unit": "C",
     "base": 28.0, "step": 0.5, "min": -40, "max": 100},
    {"sensor_id": "T-02", "type": "temperature", "unit": "C",
     "base": 24.0, "step": 0.5, "min": -40, "max": 100},
    {"sensor_id": "H-01", "type": "humidity", "unit": "%",
     "base": 55.0, "step": 2.0, "min": 0, "max": 100},
    {"sensor_id": "A-01", "type": "air_quality", "unit": "AQI",
     "base": 80.0, "step": 5.0, "min": 0, "max": 500},
]

for sensor in SENSORS:
    sensor["value"] = sensor["base"]


def make_reading(sensor):
    nudge = random.uniform(-sensor["step"], sensor["step"])
    pull = (sensor["base"] - sensor["value"]) * 0.1

    new_value = sensor["value"] + pull + nudge
    new_value = max(sensor["min"], min(sensor["max"], new_value))

    sensor["value"] = new_value

    return {
        "sensor_id": sensor["sensor_id"],
        "type": sensor["type"],
        "value": round(new_value, 1),
        "unit": sensor["unit"],
    }


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect(BROKER, PORT)
client.loop_start()

print("Multi-sensor simulator started!")
print("Muted sensors:", MUTED if MUTED else "None")

try:
    while True:
        for sensor in SENSORS:

            # Skip sensors selected for muting
            if sensor["sensor_id"] in MUTED:
                continue

            reading = make_reading(sensor)

            topic = f"sensors/{reading['type']}/{reading['sensor_id']}"

            client.publish(topic, json.dumps(reading))

            print("Sent:", topic, reading)

        time.sleep(INTERVAL)

except KeyboardInterrupt:
    print("\nStopping simulator")

finally:
    client.loop_stop()
    client.disconnect()
    print("MQTT disconnected")
