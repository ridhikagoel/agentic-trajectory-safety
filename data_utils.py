"""Shared loading and train/test splitting for all three detectors."""

import json
import random
from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"


def load_trajectories():
    rows = []
    with open(DATA_DIR / "trajectories.jsonl") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def load_cred_scope():
    with open(DATA_DIR / "cred_scope.json") as f:
        return {c: set(hosts) for c, hosts in json.load(f).items()}


def train_test_split(rows, test_frac=0.2, seed=7):
    rng = random.Random(seed)
    shuffled = rows[:]
    rng.shuffle(shuffled)
    n_test = int(len(shuffled) * test_frac)
    return shuffled[n_test:], shuffled[:n_test]
