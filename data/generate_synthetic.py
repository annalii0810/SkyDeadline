from pathlib import Path

import numpy as np
import pandas as pd


def generate_dataset(seed=42):
    rng = np.random.default_rng(seed)

    rows = []

    # Generate 1,000 normal telemetry readings
    for i in range(1000):
        rows.append({
            "gps_error": max(0, rng.normal(2, 0.8)),
            "roll": rng.normal(0, 3),
            "pitch": rng.normal(0, 3),
            "altitude": rng.normal(50, 1),
            "label": 0
        })

    # Generate 200 synthetic attack readings
    for i in range(200):
        rows.append({
            "gps_error": max(0, rng.normal(15, 4)),
            "roll": rng.normal(25, 10),
            "pitch": rng.normal(15, 8),
            "altitude": rng.normal(55, 5),
            "label": 1
        })

    df = pd.DataFrame(rows)

    # Shuffle rows reproducibly
    df = df.sample(frac=1, random_state=seed).reset_index(drop=True)

    return df


if __name__ == "__main__":
    dataset = generate_dataset()

    output = Path("data/synthetic_telemetry.csv")
    output.parent.mkdir(parents=True, exist_ok=True)

    dataset.to_csv(output, index=False)

    print("SkyDeadline Synthetic Dataset")
    print("-----------------------------")
    print("Total samples:", len(dataset))
    print("Normal samples:", (dataset["label"] == 0).sum())
    print("Attack samples:", (dataset["label"] == 1).sum())
    print("Saved to:", output)