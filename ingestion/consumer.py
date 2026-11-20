
import json
import paho.mqtt.client as mqtt

from processing.validator import validate
from alerts.engine import check_reading

from storage.database import (
    get_connection,
    init_db,
    save_reading,
    save_alert
)

# MQTT Broker Configuration
BROKER = "localhost"
PORT = 1883
TOPIC = "sensors/#"


def on_connect(client, userdata, flags, reason_code, properties):

    print("Connected:", reason_code)

    client.subscribe(TOPIC)

    print("Subscribed to:", TOPIC)


def on_message(client, userdata, msg):

    # Validate incoming message
    clean, reason = validate(msg.payload)

    if clean is None:

        print("REJECTED:", reason)

        with open("rejected.log", "a", encoding="utf-8") as f:
            f.write(f"{reason} | {msg.payload!r}\n")

        return

    # Save valid sensor reading
    save_reading(conn, clean)

    print("SAVED:", clean["sensor_id"], clean["value"], clean["unit"])

    # Check whether the reading triggers an alert
    for alert in check_reading(clean):

        save_alert(conn, alert)

        print(
            "!!! ALERT:",
            alert["message"],
            "|",
            alert["sensor_id"],
            alert["value"],
            "(rule:",
            alert["threshold"] + ")"
        )


# Database connection
conn = get_connection()
init_db(conn)

# Create MQTT client
client = mqtt.Client(
    mqtt.CallbackAPIVersion.VERSION2
)

client.on_connect = on_connect
client.on_message = on_message

client.connect(BROKER, PORT)

try:
    client.loop_forever()

except KeyboardInterrupt:
    print("Stopping consumer")

finally:
    conn.close()
