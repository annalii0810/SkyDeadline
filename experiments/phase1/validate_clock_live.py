
"""Validate SkyDeadline's experiment clock against live SITL telemetry."""

import time

from pymavlink import mavutil

from experiments.phase1.experiment_clock import ExperimentClock


def main():
    clock = ExperimentClock()

    connection = mavutil.mavlink_connection(
        "udpin:127.0.0.1:14551",
        source_system=251,
        source_component=191,
    )

    try:
        heartbeat = connection.wait_heartbeat(timeout=15)

        if heartbeat is None:
            raise TimeoutError("No SITL heartbeat")

        print("SITL connected")

        deadline = time.monotonic() + 10

        while time.monotonic() < deadline:
            msg = connection.recv_match(
                type="SYSTEM_TIME",
                blocking=True,
                timeout=1,
            )

            if msg is None:
                continue

            clock.add_sample(
                msg.time_boot_ms,
                time.monotonic_ns(),
            )

        calibration = clock.calibrate()

        print("\n--- Live Clock Calibration ---")
        print("Samples:", calibration["samples"])
        print("Offset (us):", round(calibration["offset_us"], 1))
        print("Spread (us):", round(calibration["spread_us"], 1))

        # Convert a new host timestamp into estimated boot time.
        host_now = time.monotonic_ns()
        estimated_boot_us = clock.host_to_boot_us(host_now)

        print("Estimated boot time (us):", estimated_boot_us)
        print("Validation: calibration completed")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
