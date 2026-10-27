
"""SkyDeadline A1 — Scheduled GPS drift profile for SITL experiments."""

import time


class GPSDriftProfile:
    """Generate a gradually increasing horizontal GPS offset."""

    def __init__(self, drift_rate_m_s, duration_s):
        if drift_rate_m_s <= 0:
            raise ValueError("Drift rate must be positive")

        if duration_s <= 0:
            raise ValueError("Duration must be positive")

        self.drift_rate_m_s = float(drift_rate_m_s)
        self.duration_s = float(duration_s)

    def offset_at(self, elapsed_s):
        """Return north/east offsets for elapsed attack time."""
        elapsed = max(0.0, min(float(elapsed_s), self.duration_s))

        return {
            "north_m": self.drift_rate_m_s * elapsed,
            "east_m": 0.0,
        }


def dry_run(rate=0.5, duration=10.0):
    """Print the planned GPS offset without transmitting MAVLink."""
    profile = GPSDriftProfile(rate, duration)

    print("SkyDeadline A1 GPS Drift — Dry Run")
    print("Drift rate:", rate, "m/s")
    print("Duration:", duration, "s")

    for second in range(int(duration) + 1):
        offset = profile.offset_at(second)

        print(
            f"t={second:02d}s | "
            f"north={offset['north_m']:.2f}m | "
            f"east={offset['east_m']:.2f}m"
        )


if __name__ == "__main__":
    dry_run()
