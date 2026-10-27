
"""Generate the reproducible SkyDeadline Phase I.1 experiment manifest."""

import csv
import hashlib
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CONFIG = ROOT / "configs/phase1/attack_sweep.json"
OUTPUT = ROOT / "experiments/phase1/attack_manifest.csv"


def generate_manifest(config):
    """Enumerate every attack, parameter, mission, and repetition."""
    rows = []

    for attack_id, attack in config["attacks"].items():
        parameter_names = sorted(attack["parameters"])
        parameter_values = [
            attack["parameters"][name]
            for name in parameter_names
        ]

        for combination in itertools.product(*parameter_values):
            parameters = dict(zip(parameter_names, combination))

            for mission in config["missions"]:
                for repeat in range(1, config["repeats"] + 1):
                    # Stable identifiers make repeated generation identical.
                    identity = json.dumps(
                        [attack_id, parameters, mission, repeat],
                        sort_keys=True,
                    )
                    digest = hashlib.sha256(
                        identity.encode("utf-8")
                    ).hexdigest()

                    rows.append({
                        "run_id": f"{attack_id}_{digest[:12]}",
                        "attack_id": attack_id,
                        "attack_name": attack["name"],
                        "parameters": json.dumps(
                            parameters, sort_keys=True
                        ),
                        "mission": mission,
                        "repeat": repeat,
                        "seed": int(digest[:8], 16),
                        "status": "planned",
                    })

    return rows


def main():
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    rows = generate_manifest(config)

    if not rows:
        raise RuntimeError("No experiment runs generated")

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print("Manifest generated:", OUTPUT)
    print("Total planned runs:", len(rows))
    print("Unique run IDs:", len({row["run_id"] for row in rows}))


if __name__ == "__main__":
    main()
