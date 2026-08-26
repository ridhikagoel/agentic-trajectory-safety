"""Create a file-level manifest for the immutable generated datasets."""

import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data"
OUTPUT = DATA_DIR / "generation_manifest.json"
FILES = [
    "trajectories.jsonl",
    "cred_scope.json",
    "gen_train.jsonl",
    "gen_in_dist_test.jsonl",
    "gen_heldout_test.jsonl",
    "gen_pairs_meta.json",
    "stress_test/train.jsonl",
    "stress_test/test.jsonl",
    "stress_test/generation_manifest.json",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def jsonl_counts(path):
    labels = {"0": 0, "1": 0}
    rows = 0
    with open(path) as handle:
        for line in handle:
            row = json.loads(line)
            rows += 1
            labels[str(row["label"])] += 1
    return {"rows": rows, "labels": labels}


def main():
    manifest = {
        "generator_seed": 42,
        "main_split_seed": 7,
        "generalization_split_seed": 99,
        "trajectory_length": {"minimum": 8, "maximum": 20},
        "credential_to_connect_window": 6,
        "benign_subtype_probabilities": {
            "decoy_in_scope": 0.35,
            "two_credential_reads": 0.20,
            "two_connections": 0.20,
            "credential_then_out_of_window_connection": 0.25,
        },
        "stress_test": {
            "generator_seed": 31415,
            "trajectory_length": {"minimum": 14, "maximum": 32},
            "unsafe_prevalence": 0.30,
            "random_label_noise": False,
            "train_rows": 8000,
            "test_rows": 2000,
        },
        "files": {},
    }
    for name in FILES:
        path = DATA_DIR / name
        entry = {"bytes": path.stat().st_size, "sha256": sha256(path)}
        if path.suffix == ".jsonl":
            entry.update(jsonl_counts(path))
        manifest["files"][name] = entry
    with open(OUTPUT, "w") as handle:
        json.dump(manifest, handle, indent=2)
    print(f"Wrote {OUTPUT}")


if __name__ == "__main__":
    main()
