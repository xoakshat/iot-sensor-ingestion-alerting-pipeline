
import sqlite3

from storage.database import DB_PATH, get_sensor_status

conn = sqlite3.connect(DB_PATH)

# Total sensor readings
total = conn.execute(
    "SELECT COUNT(*) FROM readings"
).fetchone()[0]

print("Total rows:", total)

# Latest five readings
print("\nLatest 5:")

for row in conn.execute(
    "SELECT * FROM readings ORDER BY id DESC LIMIT 5"
):
    print(row)

# Statistics for each sensor
print("\nPer sensor (id, count, avg, min, max):")

for row in conn.execute(
    "SELECT sensor_id, COUNT(*), ROUND(AVG(value), 1), MIN(value), MAX(value) "
    "FROM readings GROUP BY sensor_id"
):
    print(row)

# Total alerts
print("\nTotal alerts:")

alert_count = conn.execute(
    "SELECT COUNT(*) FROM alerts"
).fetchone()[0]

print(alert_count)

# Latest alerts
print("\nLatest alerts:")

for row in conn.execute(
    "SELECT * FROM alerts ORDER BY id DESC LIMIT 10"
):
    print(row)

# Current sensor status
print("\nSensor status:")

for sensor in get_sensor_status(conn):
    print(sensor)

conn.close()
