
"""SkyDeadline Phase I.1 — Ground-truth safety-envelope monitor."""

import json
import math
from pathlib import Path


class ViolationMonitor:
    """Track the first valid safety-envelope breach after attack onset."""

    def __init__(self, config_path):
        with Path(config_path).open(encoding="utf-8") as file:
            config = json.load(file)

        self.thresholds = config["thresholds"]
        self.attack_onset_us = None
        self.first_violation = None
        self.preexisting_violation = None
        self.last_time_us = None

    def set_attack_onset(self, time_us):
        """Register attack onset in the DataFlash TimeUS clock domain."""
        if self.attack_onset_us is not None:
            raise ValueError("Attack onset has already been recorded")

        if isinstance(time_us, bool) or not isinstance(time_us, int):
            raise TypeError("Attack onset must be an integer timestamp")

        if time_us < 0:
            raise ValueError("Attack onset cannot be negative")

        if self.last_time_us is not None and time_us < self.last_time_us:
            raise ValueError("Attack onset precedes an observed sample")

        self.attack_onset_us = time_us

    def evaluate(
        self,
        time_us,
        *,
        roll_deg=None,
        pitch_deg=None,
        altitude_m=None,
        target_altitude_m=None,
        geofence_error_m=None,
        trajectory_error_m=None,
        ekf_failsafe=None,
    ):
        """Evaluate a timestamped state sample against the safety envelope."""
        if isinstance(time_us, bool) or not isinstance(time_us, int):
            raise TypeError("Sample timestamp must be an integer")

        if time_us < 0:
            raise ValueError("Sample timestamp cannot be negative")

        if self.last_time_us is not None and time_us < self.last_time_us:
            raise ValueError("Out-of-order simulator timestamp")

        self.last_time_us = time_us

        # The episode is invalid if a safety breach preceded the attack.
        if self.preexisting_violation is not None:
            raise RuntimeError(
                "Pre-existing safety violation; episode invalid for T_v"
            )

        # Preserve the earliest post-onset violation.
        if self.first_violation is not None:
            return self.first_violation

        thresholds = self.thresholds
        violations = []

        def check(name, value, limit):
            """Add a violation when a finite metric exceeds its limit."""
            if value is None:
                return

            value = float(value)

            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")

            if value > limit:
                violations.append((name, value, limit))

        if roll_deg is not None:
            check("roll", abs(roll_deg), thresholds["max_abs_roll_deg"])

        if pitch_deg is not None:
            check("pitch", abs(pitch_deg), thresholds["max_abs_pitch_deg"])

        if altitude_m is not None and target_altitude_m is not None:
            check(
                "altitude",
                abs(float(altitude_m) - float(target_altitude_m)),
                thresholds["max_altitude_error_m"],
            )

        check(
            "geofence",
            geofence_error_m,
            thresholds["max_geofence_corridor_error_m"],
        )

        check(
            "trajectory",
            trajectory_error_m,
            thresholds["max_trajectory_error_m"],
        )

        if ekf_failsafe is True and thresholds["ekf_failsafe_is_violation"]:
            violations.append(("ekf_failsafe", 1, 0))

        if not violations:
            return None

        name, value, limit = violations[0]

        # Pre-onset observations establish whether the run was already unsafe.
        if self.attack_onset_us is None or time_us < self.attack_onset_us:
            self.preexisting_violation = {
                "type": name,
                "time_us": time_us,
            }
            return None

        self.first_violation = {
            "type": name,
            "time_us": time_us,
            "attack_onset_us": self.attack_onset_us,
            "tv_s": (time_us - self.attack_onset_us) / 1_000_000,
            "observed_value": value,
            "threshold": limit,
        }

        return self.first_violation
