"""Step 4 (cont.) - train and evaluate the LSTM detector, both splits."""

import json
import numpy as np
from pathlib import Path

from data_utils import load_trajectories, load_cred_scope, train_test_split
from generalization_check import split_pairs, build_split, N_TRAIN_PER_CLASS, N_TEST_PER_CLASS
from lstm_model import build_resource_vocab, train_model, predict

OUT_DIR = Path(__file__).parent / "results"
OUT_DIR.mkdir(exist_ok=True)


def metrics_from_probs(probs, labels, threshold=0.5):
    preds = (probs >= threshold).astype(int)
    labels = np.array(labels)
    tp = int(((preds == 1) & (labels == 1)).sum())
    fp = int(((preds == 1) & (labels == 0)).sum())
    fn = int(((preds == 0) & (labels == 1)).sum())
    tn = int(((preds == 0) & (labels == 0)).sum())
    precision = tp / (tp + fp) if (tp + fp) else float("nan")
    recall = tp / (tp + fn) if (tp + fn) else float("nan")
    fpr = fp / (fp + tn) if (fp + tn) else float("nan")
    return dict(tp=tp, fp=fp, fn=fn, tn=tn, precision=precision, recall=recall, fpr=fpr), preds


def main():
    print("=== Standard random split (matches logistic regression setup) ===")
    rows = load_trajectories()
    train_rows, test_rows = train_test_split(rows)
    vocab = build_resource_vocab(rows)
    print(f"Resource vocab size: {len(vocab)}")

    model = train_model(train_rows, vocab, epochs=8)
    probs = predict(model, test_rows, vocab)
    labels = [r["label"] for r in test_rows]
    m, preds = metrics_from_probs(probs, labels)
    print(f"LSTM on held-out test set (n={len(test_rows)}):")
    print(f"  TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']}")
    print(f"  precision={m['precision']:.3f}  recall={m['recall']:.3f}  FPR={m['fpr']:.3f}")

    np.save(OUT_DIR / "lstm_preds.npy", preds)
    np.save(OUT_DIR / "lstm_probs.npy", probs)
    with open(OUT_DIR / "lstm_metrics.json", "w") as f:
        json.dump(m, f, indent=2)

    print("\n=== Held-out (credential, host) pairs generalization check ===")
    cred_scope = load_cred_scope()
    train_pairs, heldout_pairs = split_pairs(cred_scope)
    gen_train_rows = build_split(train_pairs, cred_scope, N_TRAIN_PER_CLASS)
    in_dist_rows = build_split(train_pairs, cred_scope, N_TEST_PER_CLASS)
    heldout_rows = build_split(heldout_pairs, cred_scope, N_TEST_PER_CLASS)

    gen_vocab = build_resource_vocab(gen_train_rows + in_dist_rows + heldout_rows)
    gen_model = train_model(gen_train_rows, gen_vocab, epochs=8, seed=1)

    gen_results = {}
    for name, split_rows in [("in_distribution", in_dist_rows), ("held_out_pairs", heldout_rows)]:
        p = predict(gen_model, split_rows, gen_vocab)
        y = [r["label"] for r in split_rows]
        m, _ = metrics_from_probs(p, y)
        gen_results[name] = m
        print(f"{name}, n={len(split_rows)}:")
        print(f"  TP={m['tp']} FP={m['fp']} FN={m['fn']} TN={m['tn']}")
        print(f"  precision={m['precision']:.3f}  recall={m['recall']:.3f}  FPR={m['fpr']:.3f}")

    with open(OUT_DIR / "lstm_generalization.json", "w") as f:
        json.dump(gen_results, f, indent=2)


if __name__ == "__main__":
    main()
