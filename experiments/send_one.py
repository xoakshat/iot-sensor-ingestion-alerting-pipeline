
import json
import sys
import paho.mqtt.client as mqtt

sensor_id, kind, value, unit = sys.argv[1:5]

try:
    value = float(value)
except ValueError:
    pass

message = {
    "sensor_id": sensor_id,
    "type": kind,
    "value": value,
    "unit": unit
}

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)

client.connect("localhost", 1883)
client.loop_start()

client.publish(
    f"sensors/{kind}/{sensor_id}",
    json.dumps(message)
).wait_for_publish()

client.loop_stop()
client.disconnect()

print("sent:", message)
