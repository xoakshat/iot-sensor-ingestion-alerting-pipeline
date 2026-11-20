# IoT Sensor Ingestion & Alerting Pipeline

A Python-based IoT project that simulates multiple sensors, collects their readings using MQTT, validates incoming data, stores it in an SQLite database, detects abnormal conditions, and displays everything on a live Streamlit dashboard.

## 1. Project Overview

In an IoT environment, sensors continuously generate data such as temperature, humidity, and air quality. Simply collecting this data is not enough. We also need to validate it, store it, monitor sensor activity, and identify abnormal readings.

This project demonstrates a complete sensor data pipeline using Python and open-source technologies.

The project currently uses simulated sensors instead of physical hardware.

## 2. Objectives

- Simulate multiple IoT sensors.
- Collect sensor readings through MQTT.
- Validate incoming data before storing it.
- Reject invalid or out-of-range readings.
- Store valid readings in an SQLite database.
- Generate alerts when sensor readings cross predefined thresholds.
- Detect sensors that stop sending data.
- Display live readings, sensor status, charts, and alerts through a dashboard.
- Test important components using automated tests.

## 3. System Architecture

The project follows a simple data pipeline architecture:

```text
        IoT Sensor Simulator
                 |
                 v
          MQTT Publisher
                 |
                 v
          Mosquitto Broker
                 |
                 v
          MQTT Consumer
                 |
                 v
         Data Validation
                 |
          +------+------+
          |             |
          v             v
      Rejected       Valid Data
      Messages           |
          |              v
          v         SQLite Database
     rejected.log        |
                         v
                    Alert Engine
                         |
                         v
                    Alerts Table

        Sensor Watchdog
              |
              v
       Sensor Status Alerts

        SQLite Database
              |
              v
       Streamlit Dashboard
```

## 4. Technologies Used

| Technology | Purpose |
|---|---|
| Python | Main programming language |
| MQTT | Communication protocol for sensor messages |
| Mosquitto | MQTT message broker |
| Paho-MQTT | Python MQTT client library |
| SQLite | Database for readings and alerts |
| Pandas | Data handling and processing |
| Streamlit | Interactive dashboard |
| Pytest | Automated testing |

## 5. Sensors Simulated

The project currently simulates four sensors:

| Sensor ID | Sensor Type | Unit |
|---|---|---|
| T-01 | Temperature | °C |
| T-02 | Temperature | °C |
| H-01 | Humidity | % |
| A-01 | Air Quality | AQI |

The simulator generates changing readings every two seconds.

## 6. How the Pipeline Works

### Step 1: Sensor Simulation

The Python simulator generates readings for temperature, humidity, and air quality.

### Step 2: MQTT Communication

The simulator publishes readings to the Mosquitto broker using sensor-specific MQTT topics.

Example:

`sensors/temperature/T-01`

The MQTT consumer subscribes to `sensors/#` to receive readings from all sensor topics.

### Step 3: Data Validation

Before saving a reading, the validation module checks:

- Whether the message contains valid JSON.
- Whether all required fields are present.
- Whether the sensor type is supported.
- Whether the sensor value is numeric.
- Whether the reading falls within the allowed range.

Invalid messages are rejected and recorded in `rejected.log`.

### Step 4: Data Storage

Valid sensor readings are stored in an SQLite database named `pipeline.db`.

The database contains two main tables:

- `readings` – stores valid sensor readings.
- `alerts` – stores generated alerts.

### Step 5: Alert Detection

The alert engine checks readings against predefined thresholds.

| Sensor | Alert Condition |
|---|---|
| Temperature | Above 40°C |
| Humidity | Above 80% |
| Humidity | Below 25% |
| Air Quality | Above 150 AQI |

The system avoids repeatedly generating the same alert while a sensor remains in an alarm condition. When the reading returns to normal, the alert state resets.

### Step 6: Sensor Monitoring

The watchdog monitors the last received reading from each known sensor.

If a sensor does not send a reading for more than 10 seconds, it is marked offline and an alert is generated.

When the sensor starts sending readings again, its status returns to online.

### Step 7: Dashboard

The Streamlit dashboard displays:

- Current sensor readings.
- Online and offline sensor status.
- Total readings and alerts.
- Sensor reading history.
- Temperature, humidity, and air quality charts.
- Recent alerts.

The dashboard refreshes automatically every five seconds.

## 7. Project Structure

```text
iot-pipeline/
│
├── alerts/
│   ├── __init__.py
│   ├── engine.py
│   └── watchdog.py
│
├── dashboard/
│   └── app.py
│
├── experiments/
│   ├── send_one.py
│   ├── send_bad.py
│   ├── send_spike.py
│   └── show_rows.py
│
├── ingestion/
│   ├── __init__.py
│   └── consumer.py
│
├── processing/
│   ├── __init__.py
│   └── validator.py
│
├── simulator/
│   └── sensor_sim.py
│
├── storage/
│   ├── __init__.py
│   └── database.py
│
├── tests/
│   ├── test_alerts.py
│   └── test_validator.py
│
├── logs/
├── pipeline.db
├── rejected.log
├── requirements.txt
├── run_all.py
└── README.md
```

Note: Runtime files such as the database, logs, and virtual environment are kept locally and excluded from Git tracking.

## 8. Installation and Setup

### Prerequisites

Install the following:

- Python 3.10 or newer.
- Visual Studio Code (recommended).
- Mosquitto MQTT Broker.

### Step 1: Clone the Repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
```

Move into the project directory:

```bash
cd iot-pipeline
```

### Step 2: Create a Virtual Environment

```bash
python -m venv venv
```

Activate it on Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Start Mosquitto

Make sure the Mosquitto service is running and listening on port `1883`.

On Windows, you can start it through the Windows Services application if it is not already running.

## 9. Running the Project

Once the environment and MQTT broker are ready, run:

```bash
python run_all.py
```

The launcher starts the following components:

1. MQTT consumer.
2. Sensor watchdog.
3. Sensor simulator.
4. Streamlit dashboard.

Open the dashboard in your browser:

**http://localhost:8501**

To stop the pipeline, press `Ctrl + C` in the terminal running `run_all.py`.

## 10. Testing the Project

The project includes automated tests using Pytest.

Run the tests from the project root:

```bash
python -m pytest tests -v
```

Current test coverage includes:

- Valid sensor readings.
- Invalid JSON messages.
- Missing fields.
- Out-of-range values.
- Non-numeric values.
- Normal temperature readings.
- High-temperature alerts.
- Duplicate alert prevention.
- Alert recovery.

**Latest test result: 9 tests passed.**

### Manual Testing

The `experiments/` folder contains scripts for testing different scenarios.

Send a custom sensor reading:

```bash
python experiments/send_one.py T-02 temperature 47.3 C
```

Send invalid messages:

```bash
python experiments/send_bad.py
```

Simulate a sensor spike:

```bash
python experiments/send_spike.py
```

Inspect stored database records:

```bash
python experiments/show_rows.py
```

## 11. Key Features

- Multi-sensor simulation.
- MQTT-based real-time communication.
- Input validation and data cleaning.
- SQLite data persistence.
- Threshold-based alert generation.
- Duplicate alert prevention.
- Sensor online/offline monitoring.
- Interactive Streamlit dashboard.
- Automated testing with Pytest.
- Single-command pipeline launcher.

## 12. Current Limitations

- Sensors are simulated; physical IoT hardware is not connected.
- Messages published while the consumer is offline may be lost because the current setup does not implement persistent message delivery.
- Alert state is stored in memory and resets when the alert engine restarts.
- Sensors that have never sent a reading are not automatically known to the watchdog.
- Alert thresholds are predefined and not dynamically learned.
- Alerts are stored in the database and displayed on the dashboard; email and SMS notifications are not implemented.
- SQLite is used for local storage rather than a distributed database.

## 13. Future Improvements

Some possible improvements include:

- Integrating ESP32 or other physical IoT devices.
- Using PostgreSQL for larger data workloads.
- Adding MQTT authentication and stronger delivery guarantees.
- Implementing email or Telegram notifications.
- Adding a sensor registration system.
- Exploring machine learning for anomaly detection using collected sensor data.
- Improving alert handling with hysteresis and configurable thresholds.

## 14. Learning Outcomes

Through this project, I explored and implemented:

- Python programming and modular code organization.
- MQTT communication and message brokers.
- Data ingestion and validation.
- Relational database operations using SQLite.
- Real-time monitoring and alert logic.
- Data visualization using Streamlit.
- Automated testing using Pytest.
- Integration of multiple software components into one working pipeline.

---

**Project Type:** Academic / Learning Project  
**Domain:** Internet of Things (IoT), Data Engineering  
**Language:** Python  
**Status:** Working prototype

Built as a hands-on project to understand how sensor data can be collected, processed, monitored, and visualized through a complete data pipeline.