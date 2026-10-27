from pathlib import Path

import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler


FEATURES = ["gps_error", "roll", "pitch", "altitude"]


def main():
    data = pd.read_csv("data/synthetic_telemetry.csv")

    # Separate normal and synthetic attack readings
    normal = data[data["label"] == 0]
    attacks = data[data["label"] == 1]

    # Train only on normal readings
    train_normal, test_normal = train_test_split(
        normal, test_size=0.2, random_state=42
    )

    # Keep synthetic attacks exclusively for testing
    test_data = pd.concat(
        [test_normal, attacks], ignore_index=True
    )

    scaler = StandardScaler()
    X_train = scaler.fit_transform(train_normal[FEATURES])
    X_test = scaler.transform(test_data[FEATURES])

    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42
    )

    model.fit(X_train)

    # Isolation Forest: -1 = anomaly, 1 = normal
    predictions = model.predict(X_test)
    predictions = (predictions == -1).astype(int)

    actual = test_data["label"].to_numpy()

    print("SkyDeadline - Isolation Forest")
    print("--------------------------------")
    print("Training samples:", len(train_normal))
    print("Testing samples:", len(test_data))

    print("Accuracy:", round(accuracy_score(actual, predictions), 4))
    print("Precision:", round(precision_score(actual, predictions, zero_division=0), 4))
    print("Recall:", round(recall_score(actual, predictions, zero_division=0), 4))
    print("F1 Score:", round(f1_score(actual, predictions, zero_division=0), 4))

    tn, fp, fn, tp = confusion_matrix(
        actual, predictions, labels=[0, 1]
    ).ravel()

    print("False Positive Rate:", round(fp / (fp + tn), 4))
    print("Confusion Matrix:")
    print([[int(tn), int(fp)], [int(fn), int(tp)]])


if __name__ == "__main__":
    main()