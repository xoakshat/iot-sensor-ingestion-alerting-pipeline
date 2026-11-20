
import paho.mqtt.client as mqtt

MESSAGES = [

    # 1. Valid temperature reading
    '{"sensor_id": "T-01", "type": "temperature", "value": 28.4, "unit": "C"}',

    # 2. Numeric value stored as text
    '{"sensor_id": "T-01", "type": "temperature", "value": "29.1", "unit": "C"}',

    # 3. Missing value field
    '{"sensor_id": "T-01", "type": "temperature", "unit": "C"}',

    # 4. Null value
    '{"sensor_id": "T-01", "type": "temperature", "value": null, "unit": "C"}',

    # 5. Impossible temperature
    '{"sensor_id": "T-01", "type": "temperature", "value": -999, "unit": "C"}',

    # 6. Impossible humidity
    '{"sensor_id": "H-01", "type": "humidity", "value": 140, "unit": "%"}',

    # 7. Unknown sensor type
    '{"sensor_id": "X-99", "type": "pressure", "value": 1.0, "unit": "Pa"}',

    # 8. Non-numeric value
    '{"sensor_id": "T-01", "type": "temperature", "value": "abc", "unit": "C"}',

    # 9. Invalid JSON
    'not json at all',

    # 10. JSON array instead of object
    '[1, 2, 3]',
]

client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.connect("localhost", 1883)
client.loop_start()

for text in MESSAGES:

    client.publish(
        "sensors/test",
        text
    ).wait_for_publish()

client.loop_stop()
client.disconnect()

print("10 test messages sent successfully!")
