# SkyDeadline — Student B Telemetry Schema

## Status
Proposed schema — pending validation with Student A.

## Candidate Telemetry Fields

| Field | Purpose |
|---|---|
| timestamp_ns | Host-side monotonic timestamp |
| latitude | GPS latitude |
| longitude | GPS longitude |
| altitude | Flight altitude |
| roll | Roll angle |
| pitch | Pitch angle |
| yaw | Heading |
| groundspeed | Ground speed |
| gps_fix_type | GPS fix quality |
| ekf_status | State-estimator health indicators |

## Sampling Configuration

Proposed target sampling rate: 20 Hz

Sampling interval: 0.05 seconds

Actual message rates must be checked against SITL.

## Window Configuration

Candidate window sizes:
- 5 samples
- 10 samples
- 20 samples
- 40 samples

Initial window size: 5 samples

Window stride: 1 sample

## Initial Features

- Mean GPS error
- Maximum GPS error
- Minimum GPS error
- GPS-error standard deviation
- Average consecutive GPS-error change

## Data Requirements

- Consistent units and timestamps
- Explicit handling of missing telemetry
- Attack labels and attack-onset timestamps
- Mission and experiment identifiers
- No mixing of training and testing episodes

## Integration Point 1

Student A and Student B must confirm:
- Actual available MAVLink fields
- Sampling rates
- Units and coordinate conventions
- How GPS error is calculated
- Attack labels and timing
- Final window configuration

The schema is frozen only after joint agreement.