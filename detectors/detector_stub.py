import time
def detect_attack(telemetry):
    gps_error = telemetry["gps_error"]
    roll = telemetry["roll"]

    if gps_error > 10 or roll > 30:
        return "Attack"
    else:
        return "Normal"

if __name__ == "__main__":
    telemetry_readings = [
        {
            "gps_error": 2,
            "altitude": 50,
            "roll": 3,
            "pitch": 1
        },
        {
            "gps_error": 15,
            "altitude": 51,
            "roll": 4,
            "pitch": 2
        },
        {
            "gps_error": 4,
            "altitude": 50,
            "roll": 40,
            "pitch": 3
        }
    ]

    for telemetry in telemetry_readings:
        result = detect_attack(telemetry)
        decision_time = time.monotonic()
        print(decision_time, result)
