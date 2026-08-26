"""Five-seed evaluation of the fixed policy stress-test dataset."""

import csv
import json
import time
from pathlib import Path

import numpy as np
from sklearn.linear_model import LogisticRegression

from baseline import predict as stateless_predict
from data_utils import load_cred_scope
from evaluate import compute_metrics, load_jsonl
from features import build_pair_vocab, extract_features
from generate_dataset import CRED_IDS, HOST_IDS
from lstm_model import build_resource_vocab, predict as lstm_predict, train_model
from stateful_rule_baseline import predict as stateful_predict

SEEDS = [7, 19, 42, 73, 101]
ROOT = Path(__file__).parent
DATA_DIR = ROOT / "data" / "stress_test"
OUT_DIR = ROOT / "results" / "five_seed_stress_test"


def metric_row(seed, detector, metrics, runtime):
    return {"training_seed": seed, "detector": detector, "n": sum(metrics[k] for k in ["tp", "fp", "fn", "tn"]),
            "tp": metrics["tp"], "fp": metrics["fp"], "fn": metrics["fn"], "tn": metrics["tn"],
            "precision": metrics["precision"], "recall": metrics["recall"], "f1": metrics["f1"],
            "fpr": metrics["fpr"], "runtime_seconds": runtime}


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    train = load_jsonl(DATA_DIR / "train.jsonl")
    test = load_jsonl(DATA_DIR / "test.jsonl")
    labels = np.array([row["label"] for row in test])
    scope = load_cred_scope()
    pair_vocab = build_pair_vocab(CRED_IDS, HOST_IDS)
    x_train = np.array([extract_features(row["steps"], pair_vocab) for row in train])
    x_test = np.array([extract_features(row["steps"], pair_vocab) for row in test])
    y_train = np.array([row["label"] for row in train])
    vocab = build_resource_vocab(train + test)
    rows = []
    predictions = []

    for seed in SEEDS:
        candidates = {}
        candidates["stateless"] = (np.array([stateless_predict(r["steps"]) for r in test]), None, 0.0)
        started = time.perf_counter()
        stateful = np.array([stateful_predict(r["steps"], scope) for r in test])
        candidates["stateful_rule"] = (stateful, None, time.perf_counter() - started)
        started = time.perf_counter()
        lr = LogisticRegression(max_iter=2000, C=1.0, random_state=seed).fit(x_train, y_train)
        lr_prob = lr.predict_proba(x_test)[:, 1]
        candidates["logistic_regression"] = ((lr_prob >= 0.5).astype(int), lr_prob, time.perf_counter() - started)
        started = time.perf_counter()
        lstm = train_model(train, vocab, epochs=8, seed=seed)
        lstm_prob = lstm_predict(lstm, test, vocab)
        candidates["lstm"] = ((lstm_prob >= 0.5).astype(int), lstm_prob, time.perf_counter() - started)

        for detector, (preds, probs, runtime) in candidates.items():
            metrics = compute_metrics(preds, labels, f"{detector} [stress, seed={seed}]")
            rows.append(metric_row(seed, detector, metrics, runtime))
            for index, (example, label, pred) in enumerate(zip(test, labels, preds)):
                predictions.append({"training_seed": seed, "detector": detector, "example_index": index,
                    "subtype": example["subtype"], "label": int(label), "prediction": int(pred),
                    "probability": "" if probs is None else float(probs[index])})

    summary = []
    for detector in ["stateless", "stateful_rule", "logistic_regression", "lstm"]:
        selected = [row for row in rows if row["detector"] == detector]
        for metric in ["precision", "recall", "f1", "fpr"]:
            values = np.array([row[metric] for row in selected], dtype=float)
            values = values[np.isfinite(values)]
            summary.append({"detector": detector, "metric": metric,
                "mean": float(np.mean(values)) if len(values) else float("nan"),
                "sample_sd": float(np.std(values, ddof=1)) if len(values) > 1 else 0.0,
                "minimum": float(np.min(values)) if len(values) else float("nan"),
                "maximum": float(np.max(values)) if len(values) else float("nan"), "n_seeds": 5})

    for filename, records in [("metrics_by_seed.csv", rows), ("summary.csv", summary), ("raw_predictions.csv", predictions)]:
        with open(OUT_DIR / filename, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(records[0]))
            writer.writeheader(); writer.writerows(records)
    with open(OUT_DIR / "run_manifest.json", "w") as handle:
        json.dump({"design": "fixed stress-test data; varied model initialization/shuffle seed", "training_seeds": SEEDS,
                   "train_rows": len(train), "test_rows": len(test), "threshold": 0.5,
                   "threshold_selection": "fixed in advance; no test-set tuning"}, handle, indent=2)


if __name__ == "__main__":
    main()
