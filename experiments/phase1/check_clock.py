
"""Check host and ArduCopter boot-clock alignment."""

import statistics
import time

from pymavlink import mavutil


def main():
    connection = mavutil.mavlink_connection(
        "udpin:127.0.0.1:14551",
        source_system=251,
        source_component=191,
    )

    samples = []

    try:
        heartbeat = connection.wait_heartbeat(timeout=15)

        if heartbeat is None:
            raise TimeoutError("No SITL heartbeat received")

        print("SITL connected")
        print("Collecting clock-alignment samples...")

        deadline = time.monotonic() + 10

        while time.monotonic() < deadline:
            msg = connection.recv_match(
                type="SYSTEM_TIME",
                blocking=True,
                timeout=1,
            )

            if msg is None:
                continue

            host_ns = time.monotonic_ns()
            boot_us = int(msg.time_boot_ms) * 1000

            samples.append((host_ns, boot_us))

    finally:
        connection.close()

    if len(samples) < 5:
        raise RuntimeError("Insufficient clock samples")

    offsets_us = [
        host_ns / 1000 - boot_us
        for host_ns, boot_us in samples
    ]

    host_elapsed = (
        samples[-1][0] - samples[0][0]
    ) / 1e9

    autopilot_elapsed = (
        samples[-1][1] - samples[0][1]
    ) / 1e6

    print("\n--- Clock Alignment Results ---")
    print("Samples:", len(samples))
    print(
        "Median clock offset (us):",
        round(statistics.median(offsets_us), 1),
    )
    print(
        "Offset spread (us):",
        round(max(offsets_us) - min(offsets_us), 1),
    )
    print("Host elapsed (s):", round(host_elapsed, 3))
    print("Autopilot elapsed (s):", round(autopilot_elapsed, 3))


if __name__ == "__main__":
    main()
