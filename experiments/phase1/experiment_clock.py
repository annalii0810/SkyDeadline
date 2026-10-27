
"""SkyDeadline Phase I.1 — Host/autopilot clock calibration."""

import statistics
import time


class ExperimentClock:
    """Estimate the offset between host monotonic and autopilot boot time."""

    def __init__(self):
        self.samples = []

    def add_sample(self, boot_time_ms, host_time_ns=None):
        """Record a received autopilot timestamp and local receipt time."""
        if host_time_ns is None:
            host_time_ns = time.monotonic_ns()

        self.samples.append((
            int(host_time_ns),
            int(boot_time_ms) * 1000,
        ))

    def calibrate(self):
        """Return clock offset and observed offset spread."""
        if len(self.samples) < 5:
            raise RuntimeError("At least five clock samples required")

        offsets = [
            host_ns / 1000 - boot_us
            for host_ns, boot_us in self.samples
        ]

        return {
            "samples": len(offsets),
            "offset_us": statistics.median(offsets),
            "spread_us": max(offsets) - min(offsets),
        }

    def host_to_boot_us(self, host_time_ns):
        """Convert host monotonic time into estimated autopilot boot time."""
        calibration = self.calibrate()
        return round(
            host_time_ns / 1000 - calibration["offset_us"]
        )
