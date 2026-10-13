# SkyDeadline — Phase I.0 Flight Results

## Student A — Systems & Simulation

Three baseline missions were completed using ArduCopter SITL.

| Mission | Result | Telemetry |
|---|---|---|
| Hover | PASS | hover_01.tlog |
| Waypoint Survey | PASS | survey_04_success.tlog |
| Orbit | PASS | orbit_01_attempt3.tlog |

## Mission 1 — Hover

- Target altitude: 10 meters
- Verified hover interval: 109.75 seconds
- Position messages: 3,149

![Hover Altitude](hover_01_plot.png)

## Mission 2 — Waypoint Survey

- Route: 10 × 10-meter rectangle
- Verified waypoints: 4/4
- Target altitude: 10 meters
- Landing and disarming confirmed

![Waypoint Survey](survey_04_success_plot.png)

## Mission 3 — Orbit

- Configured radius: 5 meters
- Estimated mean radius: 5.09 meters
- Circular trajectory visually verified

![Orbit Flight](orbit_01_attempt3_plot.png)

## Raw Telemetry

Original recordings are preserved in:

`../../data/baseline/`

## Detailed Report

[Student A Baseline Report](../../docs/phase1/student_a_baseline_report.md)

## Integration Status

Student A baseline missions are complete.

Student A+B integration remains pending.
