"""Fixed-data, varied-training-seed robustness study for Section 8."""

import csv
import json
import platform
import time
from pathlib import Path

import numpy as np
import scipy
import sklearn
import torch
from sklearn.linear_model import LogisticRegression

from baseline import predict as stateless_predict
from data_utils import load_cred_scope, load_trajectories, train_test_split
from evaluate import compute_metrics, load_jsonl, mcnemar_exact
from features import build_pair_vocab, extract_features
from generate_dataset import CRED_IDS, HOST_IDS
from lstm_model import build_resource_vocab, predict as lstm_predict, train_model
from stateful_rule_baseline import predict as stateful_predict


SEEDS = [7, 19, 42, 73, 101]
DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "results" / "five_seed_fixed_data"
SPLIT_SEED = 7


def evaluate_predictions(predictions, labels, name):
    return compute_metrics(predictions, labels, name)


def rows_for_csv(seed, split, detector, examples, labels, predictions, probabilities=None):
    probabilities = probabilities if probabilities is not None else [""] * len(labels)
    for index, (example, label, prediction, probability) in enumerate(
        zip(examples, labels, predictions, probabilities)
    ):
        yield {
            "training_seed": seed,
            "split": split,
            "detector": detector,
            "example_index": index,
            "label": int(label),
            "prediction": int(prediction),
            "probability": "" if probability == "" else float(probability),
            "trajectory_length": len(example["steps"]),
        }


def metric_row(seed, split, detector, metrics, runtime_seconds):
    return {
        "training_seed": seed,
        "split": split,
        "detector": detector,
        "n": metrics["tp"] + metrics["fp"] + metrics["fn"] + metrics["tn"],
        "tp": metrics["tp"],
        "fp": metrics["fp"],
        "fn": metrics["fn"],
        "tn": metrics["tn"],
        "precision": metrics["precision"],
        "recall": metrics["recall"],
        "fpr": metrics["fpr"],
        "runtime_seconds": runtime_seconds,
    }


def summarize(metric_rows):
    summary = []
    detectors = ["stateless", "stateful_rule", "logistic_regression", "lstm"]
    for split in ["random_test", "heldout_pairs"]:
        for detector in detectors:
            selected = [
                row for row in metric_rows
                if row["split"] == split and row["detector"] == detector
            ]
            for metric in ["precision", "recall", "fpr"]:
                values = np.array([row[metric] for row in selected], dtype=float)
                finite = values[np.isfinite(values)]
                summary.append({
                    "split": split,
                    "detector": detector,
                    "metric": metric,
                    "mean": float(np.mean(finite)) if len(finite) else float("nan"),
                    "sample_sd": float(np.std(finite, ddof=1)) if len(finite) > 1 else 0.0,
                    "minimum": float(np.min(finite)) if len(finite) else float("nan"),
                    "maximum": float(np.max(finite)) if len(finite) else float("nan"),
                    "n_seeds": len(selected),
                })
    return summary


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    scope = load_cred_scope()
    all_rows = load_trajectories()
    random_train, random_test = train_test_split(all_rows, seed=SPLIT_SEED)
    heldout_train = load_jsonl(DATA_DIR / "gen_train.jsonl")
    heldout_test = load_jsonl(DATA_DIR / "gen_heldout_test.jsonl")
    pair_vocab = build_pair_vocab(CRED_IDS, HOST_IDS)

    datasets = {
        "random_test": (random_train, random_test),
        "heldout_pairs": (heldout_train, heldout_test),
    }
    metric_rows = []
    prediction_rows = []
    mcnemar_rows = []

    for seed in SEEDS:
        print(f"\n===== training seed {seed} =====")
        for split, (train_rows, test_rows) in datasets.items():
            labels = np.array([row["label"] for row in test_rows])

            started = time.perf_counter()
            stateless = np.array([stateless_predict(row["steps"]) for row in test_rows])
            runtime = time.perf_counter() - started
            metrics = evaluate_predictions(stateless, labels, f"stateless [{split}, seed={seed}]")
            metric_rows.append(metric_row(seed, split, "stateless", metrics, runtime))
            prediction_rows.extend(rows_for_csv(seed, split, "stateless", test_rows, labels, stateless))

            started = time.perf_counter()
            stateful = np.array([stateful_predict(row["steps"], scope) for row in test_rows])
            runtime = time.perf_counter() - started
            metrics = evaluate_predictions(stateful, labels, f"stateful [{split}, seed={seed}]")
            metric_rows.append(metric_row(seed, split, "stateful_rule", metrics, runtime))
            prediction_rows.extend(rows_for_csv(seed, split, "stateful_rule", test_rows, labels, stateful))

            started = time.perf_counter()
            x_train = np.array([extract_features(row["steps"], pair_vocab) for row in train_rows])
            y_train = np.array([row["label"] for row in train_rows])
            x_test = np.array([extract_features(row["steps"], pair_vocab) for row in test_rows])
            logreg = LogisticRegression(max_iter=2000, C=1.0, random_state=seed).fit(x_train, y_train)
            logreg_probabilities = logreg.predict_proba(x_test)[:, 1]
            logreg_predictions = (logreg_probabilities >= 0.5).astype(int)
            runtime = time.perf_counter() - started
            metrics = evaluate_predictions(
                logreg_predictions, labels, f"logreg [{split}, seed={seed}]"
            )
            metric_rows.append(metric_row(seed, split, "logistic_regression", metrics, runtime))
            prediction_rows.extend(rows_for_csv(
                seed, split, "logistic_regression", test_rows, labels,
                logreg_predictions, logreg_probabilities
            ))

            started = time.perf_counter()
            resource_vocab = build_resource_vocab(train_rows + test_rows)
            lstm = train_model(train_rows, resource_vocab, epochs=8, seed=seed)
            lstm_probabilities = lstm_predict(lstm, test_rows, resource_vocab)
            lstm_predictions = (lstm_probabilities >= 0.5).astype(int)
            runtime = time.perf_counter() - started
            metrics = evaluate_predictions(lstm_predictions, labels, f"lstm [{split}, seed={seed}]")
            metric_rows.append(metric_row(seed, split, "lstm", metrics, runtime))
            prediction_rows.extend(rows_for_csv(
                seed, split, "lstm", test_rows, labels, lstm_predictions, lstm_probabilities
            ))

            if split == "heldout_pairs":
                comparison = mcnemar_exact(logreg_predictions, lstm_predictions, labels)
                mcnemar_rows.append({
                    "training_seed": seed,
                    "logreg_only_correct": comparison["b_only"],
                    "lstm_only_correct": comparison["a_only"],
                    "discordant_total": comparison["a_only"] + comparison["b_only"],
                    "exact_two_sided_p_value": comparison["p_value"],
                })

    summary_rows = summarize(metric_rows)
    for filename, rows in [
        ("metrics_by_seed.csv", metric_rows),
        ("summary.csv", summary_rows),
        ("raw_predictions.csv", prediction_rows),
        ("mcnemar_contingency.csv", mcnemar_rows),
    ]:
        with open(OUT_DIR / filename, "w", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)

    manifest = {
        "study_design": "fixed saved data and fixed splits; varied model training seed",
        "training_seeds": SEEDS,
        "main_split_seed": SPLIT_SEED,
        "random_train_trajectories": len(random_train),
        "random_test_trajectories": len(random_test),
        "heldout_train_trajectories": len(heldout_train),
        "heldout_test_trajectories": len(heldout_test),
        "python": platform.python_version(),
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "scikit_learn": sklearn.__version__,
        "torch": torch.__version__,
        "outputs": [
            "metrics_by_seed.csv", "summary.csv", "raw_predictions.csv",
            "mcnemar_contingency.csv"
        ],
    }
    with open(OUT_DIR / "run_manifest.json", "w") as handle:
        json.dump(manifest, handle, indent=2)
    print(f"\nSaved five-seed study to {OUT_DIR}")


if __name__ == "__main__":
    main()
