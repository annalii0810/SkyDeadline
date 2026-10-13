# SkyDeadline — Phase I.0
## Student A: Baseline Flight Validation

**Date:** October 13, 2026  
**Platform:** ArduCopter SITL  
**Control:** MAVProxy and PyMAVLink  
**Result:** Three baseline flight patterns completed

## Mission 1 — Hover

**Status:** PASS

- Target altitude: 10 meters
- Hover altitude: Approximately 10 meters
- Hover duration: Approximately 110 seconds, based on the plotted telemetry
- Landing: Completed
- Telemetry: Recorded

**Evidence**
- `data/baseline/hover_01.tlog`
- `data/baseline/hover_01_plot.png`

## Mission 2 — Waypoint Survey

**Status:** PASS

- Flight pattern: 10 × 10-meter rectangle
- Target altitude: 10 meters
- Waypoints verified: 4 of 4
- Waypoint tolerance: 1.5 meters
- Landing and disarming: Confirmed
- Telemetry recording: Preserved

**Evidence**
- `data/baseline/survey_04_success.tlog`
- `data/baseline/survey_04_success_plot.png`

## Mission 3 — Orbit

**Status:** PASS

- Flight pattern: Circular orbit
- Configured radius: 5 meters
- Estimated mean radius: 5.09 meters
- Landing: Completed
- Telemetry: Recorded

**Evidence**
- `data/baseline/orbit_01_attempt3.tlog`
- `data/baseline/orbit_01_attempt3_plot.png`

## Engineering Findings

1. Flight telemetry was successfully captured and preserved.
2. MAVProxy BODY_NED commands are body-relative, not fixed North/East targets.
3. Fixed LOCAL_NED coordinates provided repeatable waypoint navigation.
4. Monitoring altitude and waypoint arrival improved mission reliability.
5. Earlier unsuccessful attempts were preserved for troubleshooting.

## Phase I.0 Summary

Student A completed three baseline flight patterns:
hover, waypoint survey, and circular orbit.

The successful recordings and plots provide evidence for
baseline flight validation.

## Next Phase

Prepare Student A's flight-control and telemetry components
for integration with Student B.

Integration has not yet been performed.
