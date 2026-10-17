
import sys
import time
from pathlib import Path
from pymavlink import mavutil

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "detectors")
)
from detector_stub import detect_attack

connection = mavutil.mavlink_connection(
    "udpin:127.0.0.1:14550"
)

print("Waiting for SITL heartbeat...")
connection.wait_heartbeat(timeout=15)
print("SITL connected")

roll = None
gps_error = None
decisions = 0

deadline = time.monotonic() + 20

while time.monotonic() < deadline:
    msg = connection.recv_match(blocking=True, timeout=1)

    if msg is None:
        continue

    if msg.get_type() == "ATTITUDE":
        roll = abs(msg.roll * 180 / 3.141592653589793)

    elif msg.get_type() == "GPS_RAW_INT":
        # Placeholder proxy for testing, NOT a validated GPS error.
        if msg.eph != 65535:
            gps_error = msg.eph / 100.0

    if roll is not None and gps_error is not None:
        telemetry = {
            "gps_error": gps_error,
            "roll": roll
        }

        t_event = time.monotonic_ns()
        decision = detect_attack(telemetry)
        t_decision = time.monotonic_ns()

        print(
            f"Decision={decision} | "
            f"GPS proxy={gps_error:.2f} | "
            f"Roll={roll:.2f} deg | "
            f"Processing={(t_decision-t_event)/1e6:.3f} ms"
        )

        decisions += 1
        roll = None
        gps_error = None

print("Total decisions:", decisions)
connection.close()
