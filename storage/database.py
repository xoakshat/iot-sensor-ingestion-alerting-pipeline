
import sqlite3
from pathlib import Path
from datetime import datetime, timezone

DB_PATH = Path(__file__).resolve().parent.parent / "pipeline.db"

STATUS_TIMEOUT = 10

CREATE_READINGS = """
CREATE TABLE IF NOT EXISTS readings (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    type      TEXT NOT NULL,
    value     REAL NOT NULL,
    unit      TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
"""

CREATE_ALERTS = """
CREATE TABLE IF NOT EXISTS alerts (
    id        INTEGER PRIMARY KEY AUTOINCREMENT,
    sensor_id TEXT NOT NULL,
    type      TEXT NOT NULL,
    value     REAL NOT NULL,
    threshold TEXT NOT NULL,
    message   TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
"""

CREATE_INDEX = """
CREATE INDEX IF NOT EXISTS idx_readings_sensor_time
ON readings (sensor_id, timestamp)
"""


def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=10)
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db(conn):
    conn.execute(CREATE_READINGS)
    conn.execute(CREATE_ALERTS)
    conn.execute(CREATE_INDEX)
    conn.commit()


def save_reading(conn, reading):
    conn.execute(
        "INSERT INTO readings (sensor_id, type, value, unit, timestamp) "
        "VALUES (?, ?, ?, ?, ?)",
        (
            reading["sensor_id"],
            reading["type"],
            reading["value"],
            reading["unit"],
            reading["timestamp"],
        ),
    )
    conn.commit()


def save_alert(conn, alert):
    conn.execute(
        "INSERT INTO alerts (sensor_id, type, value, threshold, message, timestamp) "
        "VALUES (?, ?, ?, ?, ?, ?)",
        (
            alert["sensor_id"],
            alert["type"],
            alert["value"],
            alert["threshold"],
            alert["message"],
            alert["timestamp"],
        ),
    )
    conn.commit()


def get_sensor_status(conn, timeout=STATUS_TIMEOUT):
    rows = conn.execute(
        "SELECT sensor_id, MAX(timestamp) FROM readings GROUP BY sensor_id"
    ).fetchall()

    now = datetime.now(timezone.utc)
    result = []

    for sensor_id, last_seen in rows:
        age = (
            now - datetime.fromisoformat(last_seen)
        ).total_seconds()

        result.append({
            "sensor_id": sensor_id,
            "last_seen": last_seen,
            "age_seconds": round(age),
            "status": "ONLINE" if age <= timeout else "OFFLINE",
        })

    return result
