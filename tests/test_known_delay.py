
"""SkyDeadline Phase I.0 — Live UDP known-delay validation."""

import sys
import time
from pathlib import Path
from pymavlink import mavutil

sys.path.insert(
    0, str(Path(__file__).resolve().parents[1] / "detectors")
)
from detector_stub import detect_attack

DELAY_MS = 200
SAMPLES = 5
PORT = 14550

connection = mavutil.mavlink_connection(
    f"udpin:127.0.0.1:{PORT}"
)

try:
    print("Waiting for SITL heartbeat...")
    heartbeat = connection.wait_heartbeat(timeout=15)

    if heartbeat is None:
        raise RuntimeError("No SITL heartbeat received")

    print("SITL connected")
    print("Clock: time.monotonic_ns()")
    print("Injected delay:", DELAY_MS, "ms")

    measurements = []
    deadline = time.monotonic() + 30

    while len(measurements) < SAMPLES and time.monotonic() < deadline:
        msg = connection.recv_match(
            type="ATTITUDE",
            blocking=True,
            timeout=2
        )

        if msg is None:
            continue

        # Timestamp the synthetic event when telemetry is received.
        t_event_ns = time.monotonic_ns()

        # Use live roll telemetry with a synthetic GPS-error input.
        telemetry = {
            "gps_error": 15.0,
            "roll": abs(msg.roll * 180 / 3.141592653589793)
        }

        # Controlled delay before the detector decision.
        time.sleep(DELAY_MS / 1000)

        decision = detect_attack(telemetry)
        t_decision_ns = time.monotonic_ns()

        elapsed_ms = (t_decision_ns - t_event_ns) / 1_000_000
        measurements.append(elapsed_ms)

        print(
            f"Sample {len(measurements)}: "
            f"Decision={decision}, "
            f"Measured={elapsed_ms:.2f} ms"
        )

    if len(measurements) != SAMPLES:
        raise RuntimeError("Insufficient telemetry samples")

    average_ms = sum(measurements) / len(measurements)
    error_ms = average_ms - DELAY_MS

    print("\n--- Phase I.0 Delay Validation ---")
    print("Samples:", len(measurements))
    print("Expected delay:", DELAY_MS, "ms")
    print("Average measured delay:", round(average_ms, 2), "ms")
    print("Average timing error:", round(error_ms, 2), "ms")

    passed = (
        all(190 <= value <= 250 for value in measurements)
        and all(value >= DELAY_MS for value in measurements)
    )

    print("RESULT:", "PASS" if passed else "CHECK")

finally:
    connection.close()
