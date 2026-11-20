
import pandas as pd
import streamlit as st

from datetime import datetime, timedelta, timezone

from storage.database import get_connection, get_sensor_status


st.set_page_config(
    page_title="IoT Sensor Dashboard",
    layout="wide"
)


WINDOWS = {
    "Last 5 minutes": 5,
    "Last 30 minutes": 30,
    "Last 2 hours": 120,
    "Last 24 hours": 1440,
}


# Get the latest reading from each sensor
def load_latest(conn):
    return pd.read_sql_query(
        "SELECT r.sensor_id, r.type, r.value, r.unit, r.timestamp "
        "FROM readings r "
        "JOIN (SELECT sensor_id, MAX(id) AS max_id "
        "FROM readings GROUP BY sensor_id) m "
        "ON r.id = m.max_id ORDER BY r.sensor_id",
        conn,
    )


# Convert UTC timestamps to Indian Standard Time
def to_ist(series):
    return pd.to_datetime(series, utc=True).dt.tz_convert("Asia/Kolkata")


# Load historical readings within the selected time window
def load_history(conn, minutes):
    cutoff = (
        datetime.now(timezone.utc) - timedelta(minutes=minutes)
    ).isoformat(timespec="seconds")

    df = pd.read_sql_query(
        "SELECT sensor_id, type, value, timestamp "
        "FROM readings "
        "WHERE timestamp >= ? ORDER BY timestamp",
        conn,
        params=(cutoff,),
    )

    if not df.empty:
        df["timestamp"] = to_ist(df["timestamp"])

    return df


# Load the latest 20 alerts
def load_alerts(conn):
    df = pd.read_sql_query(
        "SELECT id, timestamp, sensor_id, type, value, "
        "threshold, message "
        "FROM alerts ORDER BY id DESC LIMIT 20",
        conn,
    )

    if not df.empty:
        df["timestamp"] = to_ist(df["timestamp"])

    return df


@st.fragment(run_every=5)
def render(minutes):
    conn = get_connection()

    try:
        status = get_sensor_status(conn)
        latest = load_latest(conn)
        history = load_history(conn, minutes)
        alerts = load_alerts(conn)

        total_readings = conn.execute(
            "SELECT COUNT(*) FROM readings"
        ).fetchone()[0]

        total_alerts = conn.execute(
            "SELECT COUNT(*) FROM alerts"
        ).fetchone()[0]

    finally:
        conn.close()

    if latest.empty:
        st.info("No data yet. Start the consumer and the simulator.")
        return

    # Dashboard metrics
    online = sum(
        1 for sensor in status
        if sensor["status"] == "ONLINE"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric("Sensors online", f"{online} / {len(status)}")
    c2.metric("Total readings", total_readings)
    c3.metric("Total alerts", total_alerts)

    # Current readings
    st.subheader("Current readings")

    cols = st.columns(len(latest))

    for col, (_, row) in zip(cols, latest.iterrows()):
        col.metric(
            f"{row['sensor_id']} ({row['type']})",
            f"{row['value']} {row['unit']}"
        )

    # Sensor status
    st.subheader("Sensor status")

    status_df = pd.DataFrame(status)

    status_df["status"] = status_df["status"].map({
        "ONLINE": "🟢 ONLINE",
        "OFFLINE": "🔴 OFFLINE"
    })

    st.dataframe(status_df, hide_index=True)

    # Historical charts
    st.subheader("History")

    if history.empty:
        st.info("No readings in this time window.")

    else:
        for kind in sorted(history["type"].unique()):

            st.markdown(
                f"**{kind.replace('_', ' ').title()}**"
            )

            st.line_chart(
                history[history["type"] == kind],
                x="timestamp",
                y="value",
                color="sensor_id",
            )

    # Recent alerts
    st.subheader("Recent alerts")

    if alerts.empty:
        st.success("No alerts so far.")

    else:
        st.dataframe(
            alerts,
            hide_index=True
        )


# Main dashboard page
st.title("IoT Sensor Monitoring")

st.caption(
    "Live sensor monitoring, historical readings and alerts. "
    "Refreshes every 5 seconds."
)

choice = st.sidebar.selectbox(
    "History window",
    list(WINDOWS)
)

render(WINDOWS[choice])
