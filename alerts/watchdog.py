
import time
from datetime import datetime, timezone

from storage.database import (
    get_connection,
    init_db,
    save_alert,
    get_sensor_status,
    STATUS_TIMEOUT,
)

# Check sensor status every 5 seconds
CHECK_EVERY = 5

# Remember sensors that are already offline
silent = set()


def check_silence(conn):
    new_alerts = []

    for sensor in get_sensor_status(conn):

        sensor_id = sensor["sensor_id"]

        if sensor["status"] == "OFFLINE":

            if sensor_id not in silent:

                silent.add(sensor_id)

                new_alerts.append({
                    "sensor_id": sensor_id,
                    "type": "status",
                    "value": sensor["age_seconds"],
                    "threshold": f"no data > {STATUS_TIMEOUT}s",
                    "message": "Sensor stopped sending data",
                    "timestamp": datetime.now(timezone.utc).isoformat(
                        timespec="seconds"
                    ),
                })

        else:
            # Sensor is online again: clear its offline state
            silent.discard(sensor_id)

    return new_alerts


def main():

    conn = get_connection()
    init_db(conn)

    print(
        f"Watchdog running: checking every {CHECK_EVERY}s, "
        f"timeout {STATUS_TIMEOUT}s"
    )

    try:
        while True:

            for alert in check_silence(conn):

                save_alert(conn, alert)

                print(
                    "!!! ALERT:",
                    alert["message"],
                    "|",
                    alert["sensor_id"],
                    f"(silent for {alert['value']}s)"
                )

            time.sleep(CHECK_EVERY)

    except KeyboardInterrupt:
        print("Stopping watchdog")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
