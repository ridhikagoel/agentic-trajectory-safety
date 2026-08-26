"""Step 3 (cont.) - train and evaluate the logistic regression detector."""

import json
import numpy as np
from pathlib import Path
from sklearn.linear_model import LogisticRegression

from data_utils import load_trajectories, train_test_split
from features import extract_features, build_pair_vocab

OUT_DIR = Path(__file__).parent / "results"
OUT_DIR.mkdir(exist_ok=True)


def collect_ids(rows):
    creds, hosts = set(), set()
    for r in rows:
        for step in r["steps"]:
            if step["action"] == "read_credential":
                creds.add(step["resource"])
            elif step["action"] == "connect_host":
                hosts.add(step["resource"])
    return sorted(creds), sorted(hosts)


def main():
    rows = load_trajectories()
    train_rows, test_rows = train_test_split(rows)

    cred_ids, host_ids = collect_ids(rows)
    pair_vocab = build_pair_vocab(cred_ids, host_ids)
    print(f"Pair vocabulary size: {len(pair_vocab)} ({len(cred_ids)} creds x {len(host_ids)} hosts)")

    X_train = np.array([extract_features(r["steps"], pair_vocab) for r in train_rows])
    y_train = np.array([r["label"] for r in train_rows])
    X_test = np.array([extract_features(r["steps"], pair_vocab) for r in test_rows])
    y_test = np.array([r["label"] for r in test_rows])

    clf = LogisticRegression(max_iter=2000, C=1.0)
    clf.fit(X_train, y_train)

    preds = clf.predict(X_test)
    probs = clf.predict_proba(X_test)[:, 1]

    tp = int(((preds == 1) & (y_test == 1)).sum())
    fp = int(((preds == 1) & (y_test == 0)).sum())
    fn = int(((preds == 0) & (y_test == 1)).sum())
    tn = int(((preds == 0) & (y_test == 0)).sum())

    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")

    print(f"\nLogistic regression on held-out test set (n={len(test_rows)}):")
    print(f"  TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"  precision={precision:.3f}  recall={recall:.3f}  FPR={fpr:.3f}")

    np.save(OUT_DIR / "logreg_preds.npy", preds)
    np.save(OUT_DIR / "logreg_probs.npy", probs)
    np.save(OUT_DIR / "test_labels.npy", y_test)

    with open(OUT_DIR / "logreg_metrics.json", "w") as f:
        json.dump({"tp": tp, "fp": fp, "fn": fn, "tn": tn,
                    "precision": precision, "recall": recall, "fpr": fpr}, f, indent=2)


if __name__ == "__main__":
    main()
