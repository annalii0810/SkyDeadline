import statistics


def extract_features(gps_errors):
    if len(gps_errors) < 2:
        raise ValueError("At least 2 GPS readings are required")

    mean_error = sum(gps_errors) / len(gps_errors)
    max_error = max(gps_errors)
    min_error = min(gps_errors)
    std_error = statistics.pstdev(gps_errors)

    changes = []

    for i in range(1, len(gps_errors)):
        change = gps_errors[i] - gps_errors[i - 1]
        changes.append(change)

    average_change = sum(changes) / len(changes)

    return {
        "mean_error": mean_error,
        "max_error": max_error,
        "min_error": min_error,
        "std_error": std_error,
        "average_change": average_change
    }


if __name__ == "__main__":
    gps_errors = [2, 4, 6, 8, 10]

    features = extract_features(gps_errors)

    print("SkyDeadline Feature Extraction")
    print("------------------------------")

    for name, value in features.items():
        print(f"{name}: {value:.4f}")
        