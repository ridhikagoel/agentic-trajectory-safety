"""
Persist the held-out-pairs generalization splits to disk explicitly, rather
than relying on two separate scripts drawing from the same implicit global
random stream (fragile - any stray random call in between would desync
them). This makes the final comparison reproducible and lets logistic
regression and the LSTM be evaluated on the exact same saved test examples,
which is required for a valid paired statistical test between them.
"""

import json
import random
from pathlib import Path

from data_utils import load_cred_scope
from generate_dataset import CRED_IDS, HOST_IDS, make_benign_trajectory
from generalization_check import split_pairs, make_unsafe_from_pairs

random.seed(99)

OUT_DIR = Path(__file__).parent / "data"
N_TRAIN_PER_CLASS = 4000
N_TEST_PER_CLASS = 1000


def build_split(pairs, n_per_class):
    rows = []
    for _ in range(n_per_class):
        rows.append({"label": 1, "steps": make_unsafe_from_pairs(pairs)})
    for _ in range(n_per_class):
        rows.append({"label": 0, "steps": make_benign_trajectory()})
    random.shuffle(rows)
    return rows


def write_jsonl(path, rows):
    with open(path, "w") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")


if __name__ == "__main__":
    cred_scope = load_cred_scope()
    train_pairs, heldout_pairs = split_pairs(cred_scope)

    gen_train = build_split(train_pairs, N_TRAIN_PER_CLASS)
    gen_in_dist_test = build_split(train_pairs, N_TEST_PER_CLASS)
    gen_heldout_test = build_split(heldout_pairs, N_TEST_PER_CLASS)

    write_jsonl(OUT_DIR / "gen_train.jsonl", gen_train)
    write_jsonl(OUT_DIR / "gen_in_dist_test.jsonl", gen_in_dist_test)
    write_jsonl(OUT_DIR / "gen_heldout_test.jsonl", gen_heldout_test)

    with open(OUT_DIR / "gen_pairs_meta.json", "w") as f:
        json.dump({"train_pairs": train_pairs, "heldout_pairs": heldout_pairs}, f, indent=2)

    print(f"train pairs: {len(train_pairs)}, heldout pairs: {len(heldout_pairs)}")
    print(f"gen_train: {len(gen_train)}, gen_in_dist_test: {len(gen_in_dist_test)}, "
          f"gen_heldout_test: {len(gen_heldout_test)}")
