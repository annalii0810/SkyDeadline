
"""Read-only DataFlash adapter for SkyDeadline safety validation."""

from pathlib import Path

from pymavlink import mavutil

from monitors.violation_monitor import ViolationMonitor


def validate_benign_log(log_path, config_path):
    """Check ground-truth attitude and altitude during a benign flight."""
    monitor = ViolationMonitor(config_path)
    log = mavutil.mavlink_connection(str(log_path))

    home_alt = None
    latest_ctun = None
    samples = 0
    max_altitude_error = 0.0

    try:
        while True:
            msg = log.recv_match(blocking=False)

            if msg is None:
                break

            kind = msg.get_type()

            if kind == "CTUN":
                latest_ctun = msg

            elif kind == "SIM":
                if home_alt is None:
                    home_alt = float(msg.Alt)

                if latest_ctun is None:
                    continue

                # SIM is simulator truth; CTUN.DAlt is the controller target.
                true_relative_alt = float(msg.Alt) - home_alt
                desired_alt = float(latest_ctun.DAlt)
                altitude_error = abs(true_relative_alt - desired_alt)

                max_altitude_error = max(
                    max_altitude_error, altitude_error
                )

                # Benign logs have no attack onset. Evaluate all samples
                # as pre-onset observations using an onset after this log.
                if monitor.attack_onset_us is None:
                    monitor.set_attack_onset(10**18)

                monitor.evaluate(
                    int(msg.TimeUS),
                    roll_deg=float(msg.Roll),
                    pitch_deg=float(msg.Pitch),
                    altitude_m=true_relative_alt,
                    target_altitude_m=desired_alt,
                )

                samples += 1

    finally:
        log.close()

    passed = (
        samples > 0
        and monitor.preexisting_violation is None
    )

    return {
        "samples": samples,
        "max_altitude_error_m": round(max_altitude_error, 3),
        "passed": passed,
        "preexisting_violation": monitor.preexisting_violation,
    }


if __name__ == "__main__":
    base = Path.home() / "SkyDeadline/external/ardupilot/logs"
    config = "configs/phase1/safety_envelope.json"

    missions = {
        "hover": "00000001.BIN",
        "survey": "00000008.BIN",
        "orbit": "00000005.BIN",
    }

    for mission, filename in missions.items():
        result = validate_benign_log(base / filename, config)
        print(f"{mission}: {result}")
