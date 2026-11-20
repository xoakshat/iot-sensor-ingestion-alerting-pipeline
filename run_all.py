
import os
import socket
import subprocess
import sys
import time
from pathlib import Path

BROKER = ("localhost", 1883)

PROCESSES = [
    ("consumer", ["-m", "ingestion.consumer"]),
    ("watchdog", ["-m", "alerts.watchdog"]),
    ("simulator", ["simulator/sensor_sim.py"]),
    ("dashboard", ["-m", "streamlit", "run", "dashboard/app.py"]),
]


def broker_is_up():
    try:
        socket.create_connection(BROKER, timeout=2).close()
        return True
    except OSError:
        return False


def main():
    os.chdir(Path(__file__).resolve().parent)

    if not broker_is_up():
        print(
            "Cannot reach the MQTT broker on localhost:1883. "
            "Start Mosquitto first."
        )
        return

    os.makedirs("logs", exist_ok=True)

    running = []
    reported = set()

    try:
        for name, args in PROCESSES:
            log = open(
                f"logs/{name}.log",
                "w",
                encoding="utf-8"
            )

            proc = subprocess.Popen(
                [sys.executable, "-u", *args],
                stdout=log,
                stderr=subprocess.STDOUT,
            )

            running.append((name, proc, log))

            print(f"started {name} (pid {proc.pid})")

            time.sleep(2)

        print("\nAll started. Dashboard: http://localhost:8501")
        print("Logs are in the logs/ folder. Press Ctrl+C to stop everything.")

        while True:
            time.sleep(1)

            for name, proc, _ in running:
                if proc.poll() is not None and name not in reported:
                    reported.add(name)

                    print(
                        f"WARNING: {name} exited (code {proc.returncode}). "
                        f"See logs/{name}.log"
                    )

    except KeyboardInterrupt:
        print("\nStopping...")

    finally:
        for name, proc, log in running:
            if proc.poll() is None:
                proc.terminate()

        for name, proc, log in running:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()

            log.close()

        print("Stopped.")


if __name__ == "__main__":
    main()
