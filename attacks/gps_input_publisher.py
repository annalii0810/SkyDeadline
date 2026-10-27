
"""SkyDeadline — Benign GPS_INPUT publisher for isolated SITL tests."""

import time
from pymavlink import mavutil


CONNECTION = "udpin:127.0.0.1:14551"
GPS_RATE_HZ = 5


def main():
    connection = mavutil.mavlink_connection(
        CONNECTION,
        source_system=251,
        source_component=191,
    )

    try:
        if connection.wait_heartbeat(timeout=15) is None:
            raise TimeoutError("No SITL heartbeat")

        print("Connected to isolated SITL")
        print("Collecting unmodified GPS samples (dry run)")

        deadline = time.monotonic() + 10
        count = 0

        while time.monotonic() < deadline:
            msg = connection.recv_match(
                type="GPS_RAW_INT",
                blocking=True,
                timeout=1,
            )

            if msg is None:
                continue

            count += 1

            if count % 5 == 0:
                print(
                    f"GPS fix={msg.fix_type}, "
                    f"lat={msg.lat / 1e7:.7f}, "
                    f"lon={msg.lon / 1e7:.7f}, "
                    f"alt={msg.alt / 1000:.2f}m"
                )

        print("GPS samples received:", count)
        print("Dry run complete — no GPS_INPUT transmitted")

    finally:
        connection.close()


if __name__ == "__main__":
    main()
