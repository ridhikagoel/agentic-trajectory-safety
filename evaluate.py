"""
Step 5 - final evaluation.

Reports precision/recall/FPR with Wilson 95% confidence intervals for all
three detectors on:
  (a) the standard random train/test split (the main Tier-1 comparison)
  (b) the held-out-(credential,host)-pairs generalization split, both the
      in-distribution and never-seen-pair test sets

Also runs an exact McNemar's test comparing logistic regression against the
LSTM on the held-out-pairs test set specifically, since that's where they
disagree (100% vs ~83% recall) and it's the comparison worth being able to
say is not just noise.

The baseline is not included in the significance tests: it's a deterministic
rule with 0 recall by mathematical construction (Section 6's formal
argument, not a sampling estimate), so there's no variance to test against.
"""

import json
import math
import numpy as np
from pathlib import Path
from scipy.stats import binomtest
from sklearn.linear_model import LogisticRegression

from data_utils import load_trajectories, train_test_split
from baseline import predict as baseline_predict
from stateful_rule_baseline import predict as stateful_rule_predict
from data_utils import load_cred_scope
from features import extract_features, build_pair_vocab
from lstm_model import build_resource_vocab, train_model, predict as lstm_predict
from generate_dataset import CRED_IDS, HOST_IDS

DATA_DIR = Path(__file__).parent / "data"
OUT_DIR = Path(__file__).parent / "results"
OUT_DIR.mkdir(exist_ok=True)


def load_jsonl(path):
    rows = []
    with open(path) as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def wilson_ci(k, n, z=1.96):
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z ** 2 / n
    center = (p + z ** 2 / (2 * n)) / denom
    margin = z * math.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2)) / denom
    return (max(0.0, center - margin), min(1.0, center + margin))


def compute_metrics(preds, labels, label_name=""):
    preds, labels = np.array(preds), np.array(labels)
    tp = int(((preds == 1) & (labels == 1)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    tn = int(((preds == 0) & (labels == 0)).sum())
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")
    recall_ci = wilson_ci(tp, tp + fn)
    fpr_ci = wilson_ci(fp, fp + tn)
    result = dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=precision, recall=recall,
                  recall_ci95=recall_ci, fpr=fpr, fpr_ci95=fpr_ci)
    print(f"{label_name}: n={len(labels)}  TP={tp} FP={fp} FN={fn} TN={tn}")
    print(f"  precision={precision:.3f}  recall={recall:.3f} (95% CI {recall_ci[0]:.3f}-{recall_ci[1]:.3f})"
          f"  FPR={fpr:.3f} (95% CI {fpr_ci[0]:.3f}-{fpr_ci[1]:.3f})")
    return result


def mcnemar_exact(preds_a, preds_b, labels):
    """Exact McNemar's test on the discordant pairs where the two models disagree."""
    preds_a, preds_b, labels = np.array(preds_a), np.array(preds_b), np.array(labels)
    a_correct = preds_a == labels
    b_correct = preds_b == labels
    b_only = int((a_correct & ~b_correct).sum())  # A right, B wrong
    a_only = int((~a_correct & b_correct).sum())  # A wrong, B right
    n_discordant = a_only + b_only
    if n_discordant == 0:
        return {"a_only": a_only, "b_only": b_only, "p_value": 1.0}
    res = binomtest(min(a_only, b_only), n_discordant, 0.5, alternative="two-sided")
    return {"a_only": a_only, "b_only": b_only, "p_value": res.pvalue}


def main():
    results = {}

    print("=== (a) Standard random split ===")
    rows = load_trajectories()
    train_rows, test_rows = train_test_split(rows)
    test_labels = [r["label"] for r in test_rows]

    base_preds = [baseline_predict(r["steps"]) for r in test_rows]
    results["standard_baseline"] = compute_metrics(base_preds, test_labels, "Baseline (per-action rule)")

    credential_scope = load_cred_scope()
    stateful_preds = [stateful_rule_predict(r["steps"], credential_scope) for r in test_rows]
    results["standard_stateful_rule"] = compute_metrics(
        stateful_preds, test_labels, "Baseline (stateful credential-scope rule)"
    )

    pair_vocab = build_pair_vocab(CRED_IDS, HOST_IDS)
    X_train = np.array([extract_features(r["steps"], pair_vocab) for r in train_rows])
    y_train = np.array([r["label"] for r in train_rows])
    X_test = np.array([extract_features(r["steps"], pair_vocab) for r in test_rows])
    logreg = LogisticRegression(max_iter=2000, C=1.0).fit(X_train, y_train)
    logreg_preds = logreg.predict(X_test)
    results["standard_logreg"] = compute_metrics(logreg_preds, test_labels, "Logistic regression")

    resource_vocab = build_resource_vocab(rows)
    lstm = train_model(train_rows, resource_vocab, epochs=8)
    lstm_probs = lstm_predict(lstm, test_rows, resource_vocab)
    lstm_preds = (lstm_probs >= 0.5).astype(int)
    results["standard_lstm"] = compute_metrics(lstm_preds, test_labels, "LSTM")

    print("\n=== (b) Held-out (credential, host) pairs generalization ===")
    gen_train_rows = load_jsonl(DATA_DIR / "gen_train.jsonl")
    gen_in_dist_rows = load_jsonl(DATA_DIR / "gen_in_dist_test.jsonl")
    gen_heldout_rows = load_jsonl(DATA_DIR / "gen_heldout_test.jsonl")

    gen_X_train = np.array([extract_features(r["steps"], pair_vocab) for r in gen_train_rows])
    gen_y_train = np.array([r["label"] for r in gen_train_rows])
    gen_logreg = LogisticRegression(max_iter=2000, C=1.0).fit(gen_X_train, gen_y_train)

    gen_resource_vocab = build_resource_vocab(gen_train_rows + gen_in_dist_rows + gen_heldout_rows)
    gen_lstm = train_model(gen_train_rows, gen_resource_vocab, epochs=8, seed=1)

    for split_name, split_rows in [("in_distribution", gen_in_dist_rows), ("held_out_pairs", gen_heldout_rows)]:
        labels = [r["label"] for r in split_rows]
        scope_preds = [stateful_rule_predict(r["steps"], credential_scope) for r in split_rows]
        results[f"gen_{split_name}_stateful_rule"] = compute_metrics(
            scope_preds, labels, f"Stateful rule [{split_name}]"
        )
        X = np.array([extract_features(r["steps"], pair_vocab) for r in split_rows])
        lr_preds = gen_logreg.predict(X)
        results[f"gen_{split_name}_logreg"] = compute_metrics(lr_preds, labels, f"Logreg [{split_name}]")

        lstm_probs = lstm_predict(gen_lstm, split_rows, gen_resource_vocab)
        ls_preds = (lstm_probs >= 0.5).astype(int)
        results[f"gen_{split_name}_lstm"] = compute_metrics(ls_preds, labels, f"LSTM [{split_name}]")

        if split_name == "held_out_pairs":
            mc = mcnemar_exact(lr_preds, ls_preds, labels)
            results["mcnemar_logreg_vs_lstm_heldout"] = mc
            print(f"  McNemar's test (logreg vs LSTM, held-out pairs): "
                  f"logreg-only-correct={mc['b_only']} lstm-only-correct={mc['a_only']} "
                  f"p={mc['p_value']:.6f}")

    def clean(obj):
        if isinstance(obj, dict):
            return {k: clean(v) for k, v in obj.items()}
        if isinstance(obj, (np.integer,)):
            return int(obj)
        if isinstance(obj, (np.floating,)):
            return float(obj)
        return obj

    with open(OUT_DIR / "final_results.json", "w") as f:
        json.dump(clean(results), f, indent=2)
    print(f"\nSaved full results to {OUT_DIR / 'final_results.json'}")


if __name__ == "__main__":
    main()
