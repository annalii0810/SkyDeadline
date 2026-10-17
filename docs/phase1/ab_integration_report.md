# SkyDeadline — Phase I.0 A+B Integration Report

**Milestone:** M1 — End-to-End Host Skeleton
**Platform:** ArduCopter SITL, MAVProxy, PyMAVLink, Python
**Environment:** Single Kali Linux machine
**Result:** PASS — Phase I.0 integration demonstration

## 1. Objective

Establish live SITL-to-detector telemetry over UDP, use a consistent time base for synthetic event and decision timestamps, and validate timing using a known-delay injection.

## 2. UDP Telemetry Integration

- SITL telemetry forwarded through MAVProxy to `127.0.0.1:14550`.
- Student B's MAVLink receiver successfully received live messages.
- A separate integration harness converted selected telemetry fields into detector inputs.
- The detector produced 80 decisions from live telemetry.
- All observed decisions were `Normal`.

**Result: PASS**

## 3. Time Base

The integration tests use Python's `time.monotonic_ns()` for local event and decision timestamps.

Elapsed time is computed as:

`delay_ms = (t_decision_ns - t_event_ns) / 1_000_000`

The monotonic clock avoids ordinary wall-clock adjustments and is suitable for elapsed-time measurement on the same host.

## 4. Known-Delay Injection

A controlled 200 ms delay was introduced between receipt of live SITL telemetry and execution of the detector decision.

| Sample | Measured delay |
|---|---:|
| 1 | 200.13 ms |
| 2 | 200.17 ms |
| 3 | 200.28 ms |
| 4 | 200.15 ms |
| 5 | 200.12 ms |

**Average measured delay:** 200.17 ms
**Average timing error:** +0.17 ms
**Detector result:** Attack, 5/5 samples
**Validation result:** PASS

## 5. Limitations

- The injected GPS-error value was synthetic.
- The live telemetry test used a GPS quality indicator as a temporary proxy, not a validated spoofing-error measurement.
- The timing experiment did not measure a real safety-envelope violation.
- End-to-end network latency, actual attack-detection accuracy, and mitigation latency remain unmeasured.
- Ground-truth violation monitoring and attack experiments are planned for Phase I.1.

## 6. Milestone Conclusion

The team demonstrated a working host-side SITL-to-detector telemetry pipeline over UDP and validated a shared monotonic timing convention using a controlled delay.

This establishes the Phase I.0 M1 integration skeleton.

## 7. Next Phase

Phase I.1 — Attacks and Time-to-Violation:

- Define safety-envelope thresholds.
- Implement the ground-truth violation monitor.
- Develop scheduled attack injectors.
- Record attack onset and first violation timestamps.
- Calculate time-to-violation, \(T_v\).
