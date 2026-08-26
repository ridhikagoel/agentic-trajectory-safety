"""
Generalization stress test for the logistic regression detector.

The 100% result from train_logreg.py used a random trajectory split, so
every dangerous (credential, host) pair that shows up in the test set had
almost certainly already shown up, many times, in training. That's a fair
"did the model learn the historical violation pattern" result, but it is NOT
evidence the model generalizes to a credential/host pairing it has never
seen flagged before.

This script tests that directly: split the universe of out-of-scope
(credential, host) pairs itself into a train pool and a held-out pool, then
generate trajectories so that unsafe examples in training only ever use
train-pool pairs, and unsafe examples in the held-out test set only ever use
pairs the model never saw associated with label=1 during training.

If recall collapses on the held-out-pair set, that's an honest, useful
finding, not a failure to hide: it says a feature-engineered model like this
one learns from history the same way a rule does (Section 7.2's argument),
and needs the continuous retraining / audit-log feedback loop described in
Section 6.2, not one-shot generalization to entirely novel pairings. No
model can be expected to guess an arbitrary, uncorrelated policy assignment
it has never observed any evidence about.
"""

import random
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression

from data_utils import load_cred_scope
from generate_dataset import (
    FILLER_ACTIONS, FILE_IDS, HOST_IDS, CRED_IDS, MIN_LEN, MAX_LEN, WINDOW, filler_step,
    make_benign_trajectory,
)
from features import extract_features, build_pair_vocab

random.seed(99)

N_TRAIN_PER_CLASS = 4000
N_TEST_PER_CLASS = 1000


def split_pairs(cred_scope, held_out_frac=0.2):
    train_pairs, heldout_pairs = [], []
    for cred, scope in cred_scope.items():
        out_of_scope = [h for h in HOST_IDS if h not in scope]
        random.shuffle(out_of_scope)
        n_held = max(1, int(len(out_of_scope) * held_out_frac))
        heldout_pairs += [(cred, h) for h in out_of_scope[:n_held]]
        train_pairs += [(cred, h) for h in out_of_scope[n_held:]]
    return train_pairs, heldout_pairs


def make_unsafe_from_pairs(pairs):
    length = random.randint(MIN_LEN, MAX_LEN)
    steps = [filler_step() for _ in range(length)]
    cred, bad_host = random.choice(pairs)

    p1 = random.randint(0, length - 2)
    gap = random.randint(1, min(WINDOW, length - 1 - p1))
    p2 = p1 + gap
    steps[p1] = {"action": "read_credential", "resource": cred}
    steps[p2] = {"action": "connect_host", "resource": bad_host}
    return steps


def build_split(pairs, cred_scope, n_per_class):
    rows = []
    for _ in range(n_per_class):
        rows.append({"label": 1, "steps": make_unsafe_from_pairs(pairs)})
    for _ in range(n_per_class):
        rows.append({"label": 0, "steps": make_benign_trajectory()})
    random.shuffle(rows)
    return rows


def metrics(preds, labels):
    preds, labels = np.array(preds), np.array(labels)
    tp = int(((preds == 1) & (labels == 1)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    tn = int(((preds == 0) & (labels == 0)).sum())
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=precision, recall=recall, fpr=fpr)


def main():
    cred_scope = load_cred_scope()
    train_pairs, heldout_pairs = split_pairs(cred_scope)
    print(f"Train pairs: {len(train_pairs)}, held-out pairs (never in training): {len(heldout_pairs)}")

    train_rows = build_split(train_pairs, cred_scope, N_TRAIN_PER_CLASS)
    in_dist_test_rows = build_split(train_pairs, cred_scope, N_TEST_PER_CLASS)
    heldout_test_rows = build_split(heldout_pairs, cred_scope, N_TEST_PER_CLASS)

    pair_vocab = build_pair_vocab(CRED_IDS, HOST_IDS)

    X_train = np.array([extract_features(r["steps"], pair_vocab) for r in train_rows])
    y_train = np.array([r["label"] for r in train_rows])
    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(X_train, y_train)

    for name, rows in [("in-distribution (seen pairs)", in_dist_test_rows),
                        ("held-out pairs (never seen)", heldout_test_rows)]:
        X = np.array([extract_features(r["steps"], pair_vocab) for r in rows])
        y = np.array([r["label"] for r in rows])
        preds = clf.predict(X)
        m = metrics(preds, y)
        print(f"\n{name}, n={len(rows)}:")
        print(f"  TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']}")
        print(f"  precision={m['precision']:.3f}  recall={m['recall']:.3f}  FPR={m['fpr']:.3f}")


if __name__ == "__main__":
    main()
